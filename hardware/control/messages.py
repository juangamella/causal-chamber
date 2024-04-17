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

import re

""" Classes to represent and parse the messages sent and received from
the chambers' control boards.  """

# ----------------------------------------------------------------------
# Base class


class Message:
    def __init__(self, string, regexp):
        if type(string) == bytes:
            string = string.decode(errors="ignore")
        if regexp.match(string) is None:
            raise ValueError(f'Unrecognized message string "{string}"')
        else:
            self.raw = string
        parts = string.split(",")
        self.kind = parts[0]
        self.args = parts[1:]

    def __str__(self):
        return self.raw


# ----------------------------------------------------------------------
# Experiment protocol instructions: SET, MSR, WAIT and WAIT_INPUT


class SET(Message):
    """
    Examples
    --------
    >>> msg = SET("SET,red,255")
    >>> msg
    <__main__.SET object at ...>
    >>> msg.target
    'red'
    >>> msg.value
    '255'
    >>> SET("ST,red,255")
    Traceback (most recent call last):
    ...
    ValueError: Unrecognized message string "ST,red,255"
    """

    def __init__(self, string):
        regexp = re.compile("^SET,[a-z0-9_]*,-?\d*\.?\d*$|^SET,[a-z0-9_]*,1/\d*$")
        super().__init__(string, regexp)
        self.target = self.args[0]
        self.value = self.args[1]


class MSR(Message):
    """
    Examples
    --------
    >>> msg = MSR("MSR,100,10")
    >>> msg
    <__main__.MSR object at ...>
    >>> msg.n
    100
    >>> msg.wait
    10
    >>> MSR("MR,100,10")
    Traceback (most recent call last):
    ...
    ValueError: Unrecognized message string "MR,100,10"
    """

    def __init__(self, string):
        regexp = re.compile("^MSR,\d*,\d*$")
        super().__init__(string, regexp)
        self.n = int(self.args[0])
        self.wait = int(self.args[1])


class WAIT(Message):
    """
    Examples
    --------
    >>> msg = WAIT("WAIT,100")
    >>> msg
    <__main__.WAIT object at ...>
    >>> msg.wait
    100
    >>> WAIT("MR,100,10")
    Traceback (most recent call last):
    ...
    ValueError: Unrecognized message string "MR,100,10"
    """

    def __init__(self, string):
        regexp = re.compile("^WAIT,\d*$")
        super().__init__(string, regexp)
        self.wait = int(self.args[0])


class WAIT_INPUT(Message):
    """
    Examples
    --------
    >>> WAIT_INPUT("WAIT_INPUT,")
    <__main__.WAIT_INPUT object at ...>
    >>> msg = WAIT_INPUT("WAIT_INPUT,test")
    >>> msg
    <__main__.WAIT_INPUT object at ...>
    >>> msg.prompt
    'test'
    >>> WAIT_INPUT("MR,100,10")
    Traceback (most recent call last):
    ...
    ValueError: Unrecognized message string "MR,100,10"
    """

    def __init__(self, string):
        regexp = re.compile("^WAIT_INPUT,.*$")
        super().__init__(string, regexp)
        self.prompt = self.args[0]


# ----------------------------------------------------------------------
# Responses from board


class OK(Message):
    """
    Examples
    --------
    >>> OK(b"OK,")
    <__main__.OK object at ...>
    >>> msg = OK(b"OK,DONE")
    >>> msg
    <__main__.OK object at ...>
    >>> msg.args[0]
    'DONE'
    >>> OK(b"MR,100,10")
    Traceback (most recent call last):
    ...
    ValueError: Unrecognized message string "MR,100,10"
    """

    def __init__(self, string):
        regexp = re.compile("^OK,.*$")
        super().__init__(string, regexp)


class VARIABLES_LIST(Message):
    """
    Examples
    --------
    >>> msg = VARIABLES_LIST(b"VARIABLES_LIST,counter,flag,red,green,blue,current")
    >>> msg
    <__main__.VARIABLES_LIST object at ...>
    >>> msg.variables
    ['counter', 'flag', 'red', 'green', 'blue', 'current']
    >>> VARIABLES_LIST("VARIABLES_LIST,counter,")
    Traceback (most recent call last):
    ...
    ValueError: Unrecognized message string "VARIABLES_LIST,counter,"
    >>> VARIABLES_LIST(b"MR,100,10")
    Traceback (most recent call last):
    ...
    ValueError: Unrecognized message string "MR,100,10"
    """

    def __init__(self, string):
        regexp = re.compile("^VARIABLES_LIST(,[a-zA-Z0-9_]+)+$")
        super().__init__(string, regexp)
        self.variables = self.args


class CHAMBER_CONFIG(Message):
    """
    Examples
    --------
    >>> msg = CHAMBER_CONFIG(b"CHAMBER_CONFIG,standard")
    >>> msg
    <__main__.CHAMBER_CONFIG object at ...>
    >>> msg.config
    'standard'
    >>> CHAMBER_CONFIG("CHAMBER_CONFIG,standard,asd")
    Traceback (most recent call last):
    ...
    ValueError: Unrecognized message string "CHAMBER_CONFIG,standard,asd"
    >>> VARIABLES_LIST(b"MR,100,10")
    Traceback (most recent call last):
    ...
    ValueError: Unrecognized message string "MR,100,10"
    """

    def __init__(self, string):
        regexp = re.compile("^CHAMBER_CONFIG,[a-zA-Z0-9\-]+$")
        super().__init__(string, regexp)
        self.config = self.args[0]


# class DATA(Message):
#     """
#     Examples
#     --------
#     >>> DATA("DATA,")
#     <__main__.DATA object at ...>
#     >>> string = b"DATA," + data_bytes
#     >>> msg = DATA(string)
#     >>> msg
#     <__main__.DATA object at ...>
#     >>> repr(msg.data_bytes)
#     "b'\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\xfeB\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x98B\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\xfdC\\\\x00\\\\x80\\\\xffC\\\\x00\\\\xea\\\\x95F\\\\x00\\\\xa0(E\\\\x00`\\\\x98D\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00\\\\x00@\\\\x00\\\\x00\\\\x00@\\\\x00\\\\x00\\\\x00@\\\\x00\\\\x00@@\\\\x00\\\\x00@@\\\\x00\\\\x00@@\\\\x00\\\\x00\\\\x80?\\\\x00\\\\xc0\\\\x7fD\\\\x00\\\\x00BD'"
#     >>> print(len(data_bytes))
#     112
#     >>> len(msg.data_bytes)
#     112
#     >>> DATA("MR,100,10")
#     Traceback (most recent call last):
#     ...
#     ValueError: Unrecognized message string "MR,100,10"
#     """

#     def __init__(self, string):
#         regexp = re.compile("^DATA,")
#         if type(string) == bytes:
#             super().__init__(string.decode(errors="ignore"), regexp)
#         else:
#             super().__init__(string, regexp)
#         self.raw = string
#         self.data_bytes = self.raw[5:]


# ----------------------------------------------------------------------
# Parsing function

INSTRUCTIONS = [SET, MSR, WAIT, WAIT_INPUT]
RESPONSES = [OK, VARIABLES_LIST, CHAMBER_CONFIG]  # DATA]


def parse(string, accepted=INSTRUCTIONS + RESPONSES):
    """
    Parse a string into a message:

    Examples
    --------
    >>> parse("SET,red,255")
    <__main__.SET object at ...>
    >>> MSR("MSR,100,10")
    <__main__.MSR object at ...>
    >>> parse("WAIT,100")
    <__main__.WAIT object at ...>
    >>> parse("WAIT_INPUT,test")
    <__main__.WAIT_INPUT object at ...>
    >>> parse("OK,DONE")
    <__main__.OK object at ...>

    # >>> parse("DATA,".encode() + data_bytes)
    # <__main__.DATA object at ...>

    >>> parse("TEST,hello")
    Traceback (most recent call last):
    ...
    ValueError: Unrecognized message string "TEST,hello"
    """
    if type(string) == bytes:
        string = string.decode()
    parsed = None
    for kind in accepted:
        try:
            parsed = kind(string)
            break
        except ValueError:
            continue
    if parsed is None:
        raise ValueError(f'Unrecognized message string "{string}"')
    else:
        return parsed


# ----------------------------------------------------------------------
# Doctests
if __name__ == "__main__":
    import doctest

    data_bytes = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfeB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x98B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfdC\x00\x80\xffC\x00\xea\x95F\x00\xa0(E\x00`\x98D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00@\x00\x00\x00@\x00\x00@@\x00\x00@@\x00\x00@@\x00\x00\x80?\x00\xc0\x7fD\x00\x00BD"
    doctest.testmod(
        extraglobs={"data_bytes": data_bytes},
        verbose=True,
        optionflags=doctest.ELLIPSIS,
    )
