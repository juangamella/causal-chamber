# MIT License

# Copyright (c) 2023 Juan L. Gamella

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import binascii
import enum
from numpy.random import default_rng

"""Implements the transmission of segments over the serial with error
control & acknowledgement. Would correspond to the Transport layer of
the OSI model. The next (lower) layer is implemented in packet.py"""

MAX_INT = 2**32
BYTE_ORDER = "little"
# 200 milliseconds
ACK_TIMEOUT = 0.1

# TODO: wrap around max int?


class State(enum.Enum):
    LISTENING = 0
    SYN_RECEIVED = 1
    ESTABLISHED = 2


class Segment:
    def __init__(self, number, ack_number=0, ack=False, syn=False, data=b""):
        # Store class attributes
        if number < 0:
            raise ValueError("Sequence number should be non-negative")
        self.number = number
        if ack_number < 0:
            raise ValueError("ACK number should be non-negative")
        self.ack_number = ack_number
        self.ack = ack
        self.syn = syn
        if data is None:
            self.data = b""
        elif type(data) != bytes:
            raise TypeError('"data" should be a sequence of bytes')
        else:
            self.data = data

    def __str__(self):
        return f"<num={self.number},ack_num={self.ack_number},ACK={int(self.ack)},SYN={int(self.syn)},{self.data}>"


def encode(segment):
    """
    Examples
    --------
    >>> seg = Segment(3)
    >>> b = encode(seg)
    >>> print(decode(b))
    <num=3,ack_num=0,ACK=0,SYN=0,b''>

    >>> seg = Segment(10,ack=True,data=b"test")
    >>> b = encode(seg)
    >>> print(decode(b))
    <num=10,ack_num=0,ACK=1,SYN=0,b'test'>

    >>> seg = Segment(11,10,ack=True,syn=True,data=b"test")
    >>> b = encode(seg)
    >>> print(decode(b))
    <num=11,ack_num=10,ACK=1,SYN=1,b'test'>

    """
    # Flags byte
    #   0 - ACK
    #   1 - SYN
    flags = 1 * segment.ack + 2 * segment.syn
    flags = flags.to_bytes(length=1, byteorder=BYTE_ORDER, signed=False)
    # Sequence number bytes
    number = segment.number.to_bytes(length=4, byteorder=BYTE_ORDER, signed=False)
    # Ack number bytes
    ack_number = segment.ack_number.to_bytes(
        length=4, byteorder=BYTE_ORDER, signed=False
    )
    # Assemble
    segment_bytes = flags + number + ack_number + segment.data
    # Compute checksum
    checksum = binascii.crc32(segment_bytes).to_bytes(
        length=4, byteorder=BYTE_ORDER, signed=False
    )
    segment_bytes += checksum
    return segment_bytes


def decode(segment_bytes):
    """
    Examples
    --------
    >>> seg = Segment(11,10,ack=True,syn=True,data=b"test")
    >>> b = encode(seg)
    >>> b = bytearray(b)
    >>> b[-1] = 0
    >>> b = bytes(b)
    >>> decode(b)
    Traceback (most recent call last):
    ...
    UserWarning: Received checksum "14103450" does not match computed one "2883007386"

    """
    # Check for errors
    checksum = int.from_bytes(segment_bytes[-4:], byteorder=BYTE_ORDER, signed=False)
    rest = segment_bytes[:-4]
    computed_checksum = binascii.crc32(rest)
    if checksum != computed_checksum:
        raise UserWarning(
            f'Received checksum "{checksum}" does not match computed one "{computed_checksum}"'
        )
    # Cut into the appropriate pieces
    flags = rest[0]
    ack = flags & 1
    syn = (flags >> 1) & 1
    number = int.from_bytes(rest[1:5], byteorder=BYTE_ORDER, signed=False)
    ack_number = int.from_bytes(rest[5:9], byteorder=BYTE_ORDER, signed=False)
    data = rest[9:]

    return Segment(number, ack_number, ack, syn, data)


class TransportLayer:
    def __init__(self, packet_layer, log_fun=print, verbose=0):
        self.packet_layer = packet_layer
        self.last_acknowledged = 4294967295 - 1
        self.last_delivered = 4294967295 - 1
        self.verbose = verbose
        # Stats counters
        self.unexpected = 0
        self.ack_resends = 0
        self.resends = 0
        self.failed_checksums = 0
        self.ack_timeouts = 0

        # Wrap log function to filter by verbosity
        def log(string, verbosity_level=1, **kwargs):
            if verbosity_level <= self.verbose:
                log_fun(string, **kwargs)

        self.log = log

    def _send(self, segment):
        self.packet_layer.send(encode(segment))
        self.log(f"  SENT segment: {segment}", 2)

    def _receive(self, timeout=None):
        try:
            packet = self.packet_layer.receive(timeout)
            segment = decode(packet)
            self.log(f"  RECEIVED segment: {segment}", 2)
            return segment
        except UserWarning as e:  # Timed-out
            self.log(f"  {e}", 1)
            return None
        except binascii.Error as e:  # Could not decode base64
            self.log(f"Error decoding packet:  {e}", 1)
            return None

    def send(self, data):
        if type(data) == str:
            data = data.encode()
        # Encode into segment
        segment_to_send = Segment(number=(self.last_delivered + 1) % MAX_INT, data=data)
        # Send & acknowledgement
        acknowledged = False
        while not acknowledged:
            self._send(segment_to_send)
            try:
                reply = self._receive(timeout=ACK_TIMEOUT)
                if reply is None:
                    # i.e. checksum failed
                    self.failed_checksums += 1
                elif reply.ack and reply.ack_number == segment_to_send.number:
                    # Received acknowledgement
                    self.last_delivered = segment_to_send.number
                    self.resends += 1
                    acknowledged = True
                elif not reply.ack and reply.number == self.last_acknowledged:
                    # Reply was repetition of an already acknowledged segment; resend the acknowledgement
                    ack_segment = Segment(
                        self.last_delivered, self.last_acknowledged, ack=True
                    )
                    self._send(ack_segment)
                    self.ack_resends += 1
                else:
                    # Unexpected segment
                    self.unexpected += 1
                    self.log(f"    unexpected segment: {reply}", 0)
            except UserWarning as e:
                self.log(f"    ACK reception timed out: {e}", 1)
                self.ack_timeouts += 1
        self.resends -= 1

    def receive(self):
        acknowledged = False
        while not acknowledged:
            segment = self._receive()
            if segment is None:
                pass
            elif (
                not segment.ack
                and segment.number == (self.last_acknowledged + 1) % MAX_INT
            ):
                # The expected case: we receive a segment with the
                # number following our last acknowledgement
                ack_segment = Segment(self.last_delivered, segment.number, ack=True)
                self._send(ack_segment)
                self.last_acknowledged = (self.last_acknowledged + 1) % MAX_INT
                acknowledged = True
                # Return data
                return segment.data
            elif not segment.ack and segment.number == self.last_acknowledged:
                # We receive a segment which we already acknowledged,
                # i.e. the previous acknowledgement was lost. Resend
                # it.
                ack_segment = Segment(self.last_delivered, segment.number, ack=True)
                self._send(ack_segment)
                self.ack_resends += 1
            else:
                self.unexpected += 1
                self.log(f"    unexpected segment {segment}", 0)

    def __str__(self):
        string = "TRANSPORT LAYER STATE"
        string += "n---------------------"
        string += f"\n  last delivered sequence number = {self.last_delivered}"
        string += f"\n  last acknowledged sequence number = {self.last_acknowledged}"
        string += f"\n  unexpected segments = {self.unexpected}"
        string += f"\n  resent ACK segments = {self.ack_resends}"
        string += f"\n  resent (non-ACK) segments = {self.resends}"
        string += f"\n  failed checksums = {self.failed_checksums}"
        string += f"\n  ACK timeouts = {self.ack_timeouts}"
        return string


# ----------------------------------------------------------------------
# Doctests
if __name__ == "__main__":
    import doctest

    doctest.testmod(
        extraglobs={},
        verbose=True,
        optionflags=doctest.ELLIPSIS,
    )
