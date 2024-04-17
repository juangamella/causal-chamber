import serial
from control.serial.packet import PacketLayer
import time
import base64

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

with serial.Serial("/dev/ttyACM0", 500000, timeout=None) as ser:
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    layer = PacketLayer(ser, verbose=3)
    print(ser.read(1))
    for line in lines:
        print()
        layer.send(line.encode())
        response = layer.receive()
        assert response == line.encode()
        # time.sleep(0.1)
