# Copyright 2021 Juan L Gamella

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import serial
import time
import argparse
import sys
import numpy as np
import control.protocol as prtcl
from control.board import Board
import control.camera as camera
from datetime import datetime
import os

# Parse parameters
arguments = {
    "delay": {"default": 100, "type": int},
    "baud_rate": {"default": 500000, "type": int},
    "port": {"default": "/dev/ttyACM0", "type": str},
    "verbose": {"default": 1, "type": int},
    "protocol": {"type": str},
    "output_path": {"type": str, "default": "data_raw/"},
    "confirm": {"type": bool, "default": False},
}

parser = argparse.ArgumentParser(description="Run experiments")
for name, params in arguments.items():
    required = True
    if params["type"] == bool:
        options = {"action": "store_true"}
    else:
        options = {"action": "store", "type": params["type"]}
    if "default" in params:
        options["default"] = params["default"]
        required = False
    parser.add_argument("--" + name, dest=name, required=required, **options)

args = parser.parse_args()

# ----------------------------------------------------------------------
# Set-up camera


def print_csv(observations, file):
    observations = np.atleast_2d(observations)
    for obs in observations:
        string = ",".join(["%s" % v for v in obs])
        print(string, file=file)


camera_instructions = "Please set camera parameters:\n"
camera_instructions += "  WIFI CONNECTIVITY\n"
camera_instructions += "  MANUAL FOCUS\n"
camera_instructions += "  Set to MIN. FOCUS DISTANCE\n"
camera_instructions += "  COLOR BALANCE: DAYLIGHT\n"
camera_instructions += "  JPG ONLY\n"
camera_instructions += "  1:1 FORMAT\n"
camera_instructions += "  LOW JPG QUALITY, 4MPX\n"
camera_instructions += "  SILENT SHUTTER\n"
camera_instructions += "  SINGLE SHOT\n"
print(camera_instructions, file=sys.stderr)
if args.confirm:
    input("\nPress ENTER when ready")

cam = camera.Camera()

CAM_SET_DELAY = 1  # Wait 1 second before and after setting a camera parameter

camera_variables = ["aperture", "iso", "shutter_speed"]

# ----------------------------------------------------------------------
# Main loop

protocol_name = args.protocol.split("/")[-1]
protocol_name = protocol_name.split(".txt")[0]
timestamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
log_filename = "logs/%s_%s.log" % (timestamp, protocol_name)
# Make directories
path = args.output_path + timestamp + "_" + protocol_name + "/"
os.mkdir(path)
os.mkdir(path + "images_originals/")
output_filename = path + timestamp + "_" + protocol_name + "_raw.csv"
print(f'\nSaving data to "{output_filename}"\n', file=sys.stderr)

aperture = None
iso = None
shutter_speed = None


with open(output_filename, "w") as output_file:
    with open(log_filename, "w") as logfile:

        def log(msg, end="\n"):
            print(msg, end=end, file=sys.stderr)
            print(msg, end=end, file=logfile)
            sys.stderr.flush()
            sys.stdout.flush()

        log(args)

        # Open port and execute protocol
        log("Opening port %s at baud rate %d" % (args.port, args.baud_rate))
        with serial.Serial(args.port, args.baud_rate, timeout=None) as ser:
            board = Board(
                serial=ser, output_file=None, log_fun=log, verbose=args.verbose
            )

            # Write header with variable names
            header = ",".join(board.variables + camera_variables)
            print(header, file=output_file)
            output_file.flush()

            # Load and parse protocol
            log("Loading and parsing protocol")
            protocol = prtcl.load(args.protocol, board.variables + camera_variables)
            log("Protocol loaded")

            start_time = time.time()
            # Go through protocol, executing each instruction
            for i, instruction in enumerate(protocol):
                if instruction.kind == "SET" and instruction.target == "aperture":
                    log("  Setting camera aperture to", instruction.value)
                    aperture = camera.to_float(instruction.value)
                    time.sleep(CAM_SET_DELAY)
                    cam.set_aperture(instruction.value)
                    time.sleep(CAM_SET_DELAY)
                    cam.set_aperture(instruction.value)
                    time.sleep(CAM_SET_DELAY)
                    continue
                elif instruction.kind == "SET" and instruction.target == "iso":
                    log("  Setting camera ISO to", instruction.value)
                    iso = camera.to_float(instruction.value)
                    time.sleep(CAM_SET_DELAY)
                    cam.set_iso(instruction.value)
                    time.sleep(CAM_SET_DELAY)
                    cam.set_iso(instruction.value)
                    time.sleep(CAM_SET_DELAY)
                    continue

                elif (
                    instruction.kind == "SET" and instruction.target == "shutter_speed"
                ):
                    log("  Setting camera shutter-speed to", instruction.value)
                    shutter_speed = camera.to_float(instruction.value)
                    time.sleep(CAM_SET_DELAY)
                    cam.set_shutter_speed(instruction.value)
                    time.sleep(CAM_SET_DELAY)
                    cam.set_shutter_speed(instruction.value)
                    time.sleep(CAM_SET_DELAY)
                elif instruction.kind == "MSR":
                    observations = board.execute_instruction(instruction)
                    camera_variables = np.tile(
                        [aperture, iso, shutter_speed], (len(observations), 1)
                    )
                    observations = np.hstack([observations, camera_variables])
                    print_csv(observations, file=output_file)
                    output_file.flush()
                else:
                    board.execute_instruction(instruction)

            # Tell board to reset and close serial connection
            board.reset()
            log(
                'Ran experiment for protocol "%s" in %0.2f seconds. Stored results in "%s"'
                % (args.protocol, time.time() - start_time, output_filename)
            )
