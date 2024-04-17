import serial
from control.serial.packet import PacketLayer
import control.serial.segment as segment
import timeit
import base64
import numpy as np
import os

lines = [
    "I like to think (and",
    "the sooner the better!)",
    "of a cybernetic meadow",
    "where mammals and computers",
    "live together in mutually",
    "programming harmony",
    "like pure water",
    "touching clear sky.",
    "",
    "I like to think",
    "(right now, please!)",
    "of a cybernetic forest",
    "filled with pines and electronics",
    "where deer stroll peacefully",
    "past computers",
    "as if they were flowers",
    "with spinning blossoms.",
] * 100

a = 12314081

segments = [
    segment.Segment(11, 10, ack=True, data=b"test"),
    segment.Segment(10, ack=True, data=b"test"),
    segment.Segment(3),
    segment.Segment(3),
    segment.Segment(11, 10, ack=True, data=b"also a test"),
    segment.Segment(
        11, 10, ack=True, data=a.to_bytes(length=4, byteorder="little", signed=False)
    ),
]

n_bytes = 1
N = 1024
sent_data = [os.urandom(n_bytes) for _ in range(N)]
with serial.Serial("/dev/ttyACM0", 1000000, timeout=None) as ser:
    print("PORT OPEN")

    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # Send reset signal to arduino
    ser.setDTR(False)
    ser.setDTR(True)

    layer = PacketLayer(ser, verbose=0)
    transport_layer = segment.TransportLayer(layer, verbose=2)
    print(ser.read(1))
    start = timeit.default_timer()
    # Echo test
    # for seg in segments:
    #     b = segment.encode(seg)
    #     layer.send(b)
    #     csum = b"v\xd6\xee\xc1"
    #     print(f"Sent checksum: {int.from_bytes(csum, byteorder='little')}")
    #     response = layer.receive()
    #     print(seg)
    #     print(segment.decode(response))
    #     assert str(seg) == str(segment.decode(response))
    # # Reception & acknowledgement test
    # while True:
    #     print(
    #         f"STATE: num={transport_layer.last_delivered}, ack_num={transport_layer.last_acknowledged}"
    #     )
    #     msg = transport_layer.receive()
    #     print(msg)
    # Duplex test
    # Send numbers

    # print("SENDING BYTE STRINGS")
    # for i, data in enumerate(sent_data):
    #     transport_layer.send(data)
    #     print("sent", i, data)
    # # Receive them back
    # print("RECEIVING BYTE STRINGS")
    # for i, sent in enumerate(sent_data):
    #     data = transport_layer.receive()
    #     rec_n = int.from_bytes(data, byteorder="little", signed=False)
    #     # print(i, ":", sent, data)
    #     assert sent == data

    for line in lines:
        print(len(line), line.encode())
        try:
            transport_layer.send(line.encode())
        except Exception as e:
            print(e)
            continue
        reply = transport_layer.receive().decode()
        print(len(reply), reply.encode())
        assert line == reply
    print(transport_layer)
    print(f"{timeit.default_timer() - start} seconds")
