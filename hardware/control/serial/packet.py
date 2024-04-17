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

import base64
import enum
from serial import SerialTimeoutException

"""Implements the transmission of packets over the serial,
i.e. encodes/decodes messages into base64 and sends/receives them
using pythons pySerial. Corresponds to the Network layers and below of
the OSI Model (pySerial would be the data link layer)"""


START_SYMBOL = b"\0"
END_SYMBOL = b"\4"
ARDUINO_BUFFER_SIZE = 64

WRITE_TIMEOUT = 0.1  # 100 milliseconds


class State(enum.Enum):
    WAITING_FOR_START = 1
    READING = 2
    DATA_PARSED = 3


class PacketLayer:
    def __init__(self, ser, log_fun=print, verbose=0, discarded="warn"):
        """
        Parameters
        ----------
        serial : serial.Serial
            The serial connection object, obtained from calling
            serial.Serial (see pySerial library).
        log_fun : function, default=print
            The function used to log any debug messages, must take a
            string as first argument.
        verbose : int
            Whether to print sent/received messages and
            debug traces. Higher values correspond to increased
            verbosity: 0 - no output, 1 - Log sent/received data, 2 -
            raw messages sent/received through the serial object.
        discarded : {"ignore", "warn", "raise"}
            What to do when bytes are received outside of a start/end
            symbol. "ignore" does nothing, "warn" logs a warning,
            "raise" raises an exception.

        """
        # Set class attributes
        self.serial = ser
        self.verbose = verbose
        self.discarded = discarded

        # Wrap log function to filter by verbosity
        def log(string, verbosity_level=0, **kwargs):
            if verbosity_level <= self.verbose:
                log_fun(string, **kwargs)

        self.log = log

        # Set write timeout
        self._set_write_timeout(WRITE_TIMEOUT)

    def send(self, data):
        """Encode and send a message to the board over serial"""
        msg = START_SYMBOL + base64.b64encode(data) + END_SYMBOL
        if len(msg) > ARDUINO_BUFFER_SIZE:
            raise ValueError(
                f"Attempting to send a packet which is larger ({len(msg)} > {ARDUINO_BUFFER_SIZE}) than the arduino software buffer size."
            )
        try:
            self.serial.write(msg)
            self.serial.flush()
        except SerialTimeoutException as e:
            self.log(f"Serial write timed out: {e}")
        self.log(f'      SENT: "{data}"', 1)
        self.log(f'      SENT (raw, {len(msg)} bytes): "{msg}"', 2)

    def receive(self, timeout=None):
        """Read and decode a message from the serial connection"""
        self._set_timeout(timeout)
        state = State.WAITING_FOR_START
        msg = b""
        discarded = b""
        while state != State.DATA_PARSED:
            byte = self.serial.read()
            self.log(f"      byte={byte}", 3)
            if len(byte) == 0:
                raise UserWarning(f"Packet reception timed out after {timeout} seconds")
            if state == State.READING:
                if byte == END_SYMBOL:
                    state = State.DATA_PARSED
                else:
                    msg += byte
            elif state == State.WAITING_FOR_START and byte == START_SYMBOL:
                state = State.READING
            else:
                discarded += byte
        self.log(f'      RECEIVED (raw, {len(msg)} bytes): "{msg}"', 2)
        # Decide what to do with discarded bytes
        if len(discarded) > 0:
            warning = f"Unexpected bytes outside of message symbols: {discarded}"
            if self.discarded == "raise":
                raise Exception(warning)
            elif self.discarded == "warn":
                self.log(warning, 0)  # Always log independently of verbosity
        # Return decoded message
        data = base64.b64decode(msg)  # Raises binascii.Error if incorrectly padded
        self.log(f'      RECEIVED: "{data}"', 1)
        return data

    def _set_timeout(self, timeout):
        """Set the read timeout of the serial connection"""
        settings = self.serial.get_settings()
        settings["timeout"] = timeout
        self.serial.apply_settings(settings)
        self.log(f"  Changed timeout to {timeout} seconds", 3)

    def _set_write_timeout(self, timeout):
        """Set the read timeout of the serial connection"""
        settings = self.serial.get_settings()
        settings["write_timeout"] = timeout
        self.serial.apply_settings(settings)
        self.log(f"  Changed write timeout to {timeout} seconds", 3)
