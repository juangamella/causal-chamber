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
from datetime import datetime


# Parse parameters
arguments = {
    "delay": {"default": 4000, "type": int},  # Milliseconds to wait for board to reset
    "baud_rate": {"default": 500000, "type": int},
    "port": {"default": "/dev/ttyACM0", "type": str},
    "verbose": {"default": 1, "type": int},
    "protocol": {"type": str},
    "output_path": {"type": str, "default": "data_raw/"},
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
# Main loop

protocol_name = args.protocol.split("/")[-1]
protocol_name = protocol_name.split(".txt")[0]
timestamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
log_filename = "logs/%s_%s.log" % (timestamp, protocol_name)
output_filename = args.output_path + timestamp + "_" + protocol_name + ".csv"
print(f'\nSaving data to "{output_filename}"\n', file=sys.stderr)

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
                serial=ser,
                output_file=output_file,
                log_fun=log,
                verbose=args.verbose,
            )

            # Write header with variable names
            header = ",".join(board.variables)
            print(header, file=output_file)

            # Load and parse protocol
            log("Loading and parsing protocol")
            protocol = prtcl.load(args.protocol, board.variables)
            log("Protocol loaded")

            start_time = time.time()
            # Go through protocol, executing each instruction
            for i, instruction in enumerate(protocol):
                board.execute_instruction(instruction)

            # Tell board to reset and close serial connection
            board.reset()
            time.sleep(args.delay / 1000)
            log(
                'Ran experiment for protocol "%s" in %0.2f seconds. Stored results in "%s"'
                % (args.protocol, time.time() - start_time, output_filename)
            )
            print(board.comms)
