/* ; -*- mode: C;-*-

   MIT License

   Copyright (c) 2023 Juan L. Gamella

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.
*/

#ifndef SERIAL_COMMS
#define SERIAL_COMMS

#include <Arduino.h>

/* ---------------------------------------------------------------------- */
/* Packet layer */

struct Packet {
  byte * buffer;
  unsigned int n_bytes;
  bool timeout;
  bool ok;
};

void send_packet(byte * buffer, unsigned int n_bytes);
Packet receive_packet(int timeout);

/* ---------------------------------------------------------------------- */
/* Transport layer */

struct Segment {
  bool ack;
  unsigned long int number;
  unsigned long int ack_number;
  byte * data;
  unsigned int n_bytes;
  int ok;
};

void encode_segment(byte * output_buffer, Segment segment);
Segment decode_segment(Packet packet);
unsigned int segment_length(Segment segment);
void send_data(byte * buffer, unsigned int n_bytes);
int receive_data(byte * buffer, unsigned int max_bytes);

// Wrappers for send/receive_message
void send_string(String message);
String receive_string();

#endif

