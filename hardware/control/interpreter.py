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
import argparse
import sys
from control.board import Board


# Parse parameters
arguments = {
    "baud_rate": {"default": 500000, "type": int},
    "port": {"default": "/dev/ttyACM0", "type": str},
    "verbose": {"default": 1, "type": int},
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


def log(msg, end="\n"):
    print(msg, end=end, file=sys.stderr)


# Start comms

log("Opening port %s at baud rate %d" % (args.port, args.baud_rate))
with serial.Serial(args.port, args.baud_rate, timeout=None) as ser:
    board = Board(
        serial=ser,
        output_file=None,
        log_fun=log,
        verbose=args.verbose,
    )
    while True:
        command = input(">>> ")
        board.comms.send(command)
        reply = board.comms.receive()
        print(f"  {reply}", file=sys.stderr)
