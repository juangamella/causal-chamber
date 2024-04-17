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

/*
The serial communication has 3 layers:

1: Arduino's Serial object, to read bytes from the hardware serial
   input buffer
2: The "packet" layer: reads/writes packets of bytes from/to the
   serial - a packet is a base64 encoded sequence of bytes sandwiched
   between a start (NUL) and end (EOT) byte.
3: The transport layer: Uses the packet layer to sends/receive
   "segments" with acknowledgement and error control. A segment is a
   sequence of bytes with flags and checksum fields which is then
   encoded/decoded from a packet.

This module implements layers 2 and 3.
*/

#include <Arduino.h>
#include <Base64.h>
#include "serial_comms.h"
#include "utils.h"
#include <CRC32.h>

#define ACK_TIMEOUT 100
// base64 encoding: https://www.arduino.cc/reference/en/libraries/base64/
// CRC32 checksum: https://github.com/bakercp/CRC32

//TODO: manage when packet contains non-base64 characters

/* ---------------------------------------------------------------------- */
/* Packet layer */

// Global variables needed to operate the packet parser
typedef enum ParserState {
                           WAITING_FOR_START,
                           READING,
                           PACKET_READY
};

ParserState parser_state = WAITING_FOR_START;
const char START_SYMBOL = '\0'; // NUL
const char END_SYMBOL = '\4'; // EOT
// Buffer to store bytes read from serial
const unsigned int input_buffer_size = 64;
byte input_buffer[input_buffer_size + 1];
int input_buffer_index;
// Buffer to store decoded packets (size is max size of decoding a 64
// character long base64 string)
byte packet_buffer[(6 * input_buffer_size) / 8 + 1];


/* Encodes a buffer into base64, surrounds with start/end symbols and writes to the Serial */
void send_packet(byte * buffer, size_t n_bytes) {
  int encodedLength = Base64.encodedLength(n_bytes);
  char encodedString[encodedLength];
  Base64.encode(encodedString, buffer, n_bytes);
  Serial.write(START_SYMBOL);
  Serial.write(encodedString, encodedLength);
  Serial.write(END_SYMBOL);
  Serial.flush(); // Wait until all bytes have been written
}

/* Reads a packet byte-by-byte from the serial, and decodes it into base64. A negative timeout means no timeout.*/
Packet receive_packet(int timeout) {
  unsigned long start = millis(); // For the timeout
  unsigned long now = start; // For the timeout
  while (parser_state != PACKET_READY && (timeout < 0 ||  (now - start) < timeout)) {
    // Read characters from serial if they are available
    now = millis();
    while (Serial.available() > 0) {
      char char_in = Serial.read();
      if (parser_state == READING) {
        // If state is READING
        if (char_in == END_SYMBOL) {
          // And character is the end symbol, reset parser and change state to PACKET_READY
          input_buffer[input_buffer_index] = '\0';
          parser_state = PACKET_READY;
        } else if (input_buffer_index >= input_buffer_size) {
          // Buffer size was overrun: because we expect messages
          // smaller than the buffer, we missed an end symbol. Reset
          // the parser and wait for message repeat
          parser_state = WAITING_FOR_START;
          input_buffer_index = 0;
        } else {
          // any other character (including start symbol): add to the buffer
          input_buffer[input_buffer_index] = char_in;
          input_buffer_index++;
      }        
      } else if (parser_state == WAITING_FOR_START && char_in == START_SYMBOL) {
        // Waiting for start symbol and it arrived: start parser
        parser_state = READING;
      } else {
        // Some other character arrived while waiting for start: discard it
        continue;
      }
    }
  }
  // Check end conditions
  if (parser_state == PACKET_READY) {
    // Packet was correctly parsed: decode it
    unsigned int decodedLength = Base64.decodedLength(input_buffer, input_buffer_index);
    Base64.decode(packet_buffer, input_buffer, input_buffer_index);
    Packet packet = {.buffer = packet_buffer, .n_bytes = decodedLength, .timeout=false, .ok=true};
    // Reset the parser
    parser_state = WAITING_FOR_START;
    input_buffer_index = 0;
    return packet;
  } else {
    // A timeout ocurred
    Packet packet = {.buffer=input_buffer, .n_bytes = input_buffer_index, .timeout=true, .ok=true};
    return packet;
  }
}

/* ---------------------------------------------------------------------- */
/* Transport layer */

unsigned long last_delivered = 4294967295-1;
unsigned long last_acknowledged = 4294967295-1;

/* Given a segment, calculate how many bytes it needs to be encoded */
unsigned int segment_length(Segment segment) {
  return 1 + 4 + 4 + segment.n_bytes + 4;
}

/* Compose a segment given all its pieces. The resulting encoding, in bytes:
  0 = flag byte
  1:4 = sequence number
  5:9 = ack number
  10:x = data
  x+1:x+5 = checksum
*/
void encode_segment(byte * output_buffer, Segment segment) {
  // Add flags, numbers and data
  output_buffer[0] = segment.ack ? 0x01 : 0x00;
  memcpy(&output_buffer[1], &segment.number, 4);
  memcpy(&output_buffer[5], &segment.ack_number, 4);
  memcpy(&output_buffer[9], segment.data, segment.n_bytes);
  // Compute and add checsum
  unsigned long int checksum = CRC32::calculate(output_buffer, segment.n_bytes + 9);
  memcpy(&output_buffer[segment.n_bytes + 9], &checksum, 4);  
}

/* Given a sequence of bytes encoding a segment, decode it and check
   the checksum. Encode checksum errors in field .ok */
Segment decode_segment(Packet packet) {
  // Initialize segment
  Segment segment = {.ack = false, .number = 0, .ack_number = 0, .data = 0, .n_bytes = 0, .ok = 0};
  // Check
  unsigned long int checksum = 0;
  memcpy(&checksum, &packet.buffer[packet.n_bytes-4], 4);
  unsigned long int computed_checksum = CRC32::calculate(packet.buffer, packet.n_bytes - 4);
  if (computed_checksum != checksum) {
    // Checksum is wrong, return -1 in .ok field
    segment.ok = -1;
  } else {
    segment.ack = (bool) packet.buffer[0] & 0b00000001;
    memcpy(&segment.number, &packet.buffer[1], 4);
    memcpy(&segment.ack_number, &packet.buffer[5], 4);
    segment.data = &packet.buffer[9];
    segment.n_bytes = packet.n_bytes - (1 + 4 + 4 + 4); // bytes in the data field
  }
  return segment;
}

/* Compose and send a segment acknowledging the given sequence number */
void send_ack(unsigned long number) {
  Segment ack_segment = {.ack=true, .number = last_delivered, .ack_number = number, .data = (byte *) 0x00, .n_bytes = 0, .ok=0};
  unsigned int ack_length = segment_length(ack_segment);
  byte ack_encoded[ack_length] = {0};
  encode_segment(ack_encoded, ack_segment);
  send_packet(ack_encoded, ack_length);
}

void send_data(byte * buffer, size_t n_bytes) {
  // Compose segment with the data in buffer
  Segment segment = {.ack=false, .number = last_delivered + 1, .ack_number = 0, .data = buffer, .n_bytes = n_bytes, .ok=0};
  unsigned int length = segment_length(segment);
  byte encoded[length] = {0};
  encode_segment(encoded, segment);
  bool acknowledged = false;
  while (!acknowledged) {
    send_packet(encoded, length);
    Packet packet = receive_packet(ACK_TIMEOUT);
    if (packet.ok == true && !packet.timeout) {
      Segment reply = decode_segment(packet);
      if ((reply.ok == 0) && reply.ack && reply.ack_number == segment.number) {
        // Acknowledgement was received so the segment was delivered
        last_delivered = segment.number;
        acknowledged = true;
      }
      else if ((reply.ok == 0) && !reply.ack && reply.number == last_acknowledged) {
        // We received a segment that we already acknowledged: resend acknowledgment
        send_ack(reply.number);
      } else {
        // Checksum was not correct or we received an unexpected
        // segment
        continue;
      }
    } else {
      // We could not decode the packet or we timed-out while waiting
      // to receive one
      continue;
    }
  }
}

/* Receive and acknowledge a segment from the serial
   (blocking). Returns the number of bytes in the message (that were
   written to the buffer) or -1 if the message is longer than the
   buffer's size */
int receive_data(byte * buffer, size_t max_bytes) {
  while (true) {
    Packet packet = receive_packet(-1); // No timeout
    if (packet.ok) {
      Segment segment = decode_segment(packet);
      if (segment.ok == 0 && !segment.ack && segment.number == last_acknowledged + 1) {
        // The expected case: we receive a segment with the number
        // following our last acknowledgement
        send_ack(segment.number);
        last_acknowledged += 1;
        // Return data
        if (segment.n_bytes > max_bytes) {
          memcpy(buffer, segment.data, max_bytes);
          return -1;
        } else {
          memcpy(buffer, segment.data, segment.n_bytes);
          return segment.n_bytes;
        }
      } else if (segment.ok == 0 && !segment.ack && segment.number == last_acknowledged) {
        // We receive a segment which we already acknowledged, i.e. the
        // previous acknowledgement was lost. Resend it.
        send_ack(segment.number);      
      } else {
        // Unexpected segment, i.e. an ACK segment or another with
        continue;
      }
    }
  }
}

// Buffer to store outgoing/ingoing messages as they are converted from/to String
#define MSG_BUFFER_SIZE 64

void send_string(String string) {
  send_data(string.c_str(), string.length());
}

String receive_string() {
  char message_buffer[MSG_BUFFER_SIZE+1] = {0};
  int length = receive_data(message_buffer, MSG_BUFFER_SIZE);
  if (length < 0)
    fail("er00");
  message_buffer[length] = '\0';
  return String(message_buffer);
}
