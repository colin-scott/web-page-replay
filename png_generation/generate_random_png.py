#!/usr/bin/env python

from minpng import to_png, generate_image_data
from itertools import product
import sys
import os
from random import randint, choice

# From:
#   http://mainisusuallyafunction.blogspot.com/2012/04/minimal-encoder-for-uncompressed-pngs.html
# All units are bytes
SIG = 8
IHDR = 12 + 13
IDAT_H = 12 # + data_chunk
# data_chunk = ZLIB + (DEFHEADER * num_blocks) + data_len
ZLIB = 8
DEFHEADER = 5
# num_blocks = (data_len / MAX_BLOCK) + remainder_block
# remainder_block = (data_len % MAX_BLOCK) == 0 ? 0 : 1
MAX_BLOCK = 65535
# data_len = (PIXEL_LEN * pixels) + (FILTER * height)
PIXEL_LEN = 1
# pixels = width * height
FILTER = 1
IEND = 4

# TODO(cs): somewhere here I've overshot by 2 bytes..
# TODO(cs): test whether it's always two bytes over, even for multi-block
# images.
STATIC = SIG + IHDR + IDAT_H + ZLIB + IEND - 2

def valid_size(width, height, size):
  pixels = width * height
  data_len = (PIXEL_LEN * pixels) + (FILTER * height)
  remainder_block = 0 if ((data_len % MAX_BLOCK) == 0) else 1
  num_blocks = (data_len / MAX_BLOCK) + remainder_block
  data_chunk = ZLIB + (DEFHEADER * num_blocks) + data_len
  predicted_size = data_chunk + STATIC
  return size == predicted_size

def get_dimensions(size):
  # pre: size > 0
  # Keep height to 1 (a single FILTER byte) for ease of computation.
  height = 1
  # We use an iterative algorithm to figure out how many blocks we need.
  num_blocks = 1
  remaining_dynamic = size - STATIC - ZLIB - FILTER - DEFHEADER
  data_len = 0
  while remaining_dynamic > MAX_BLOCK - DEFHEADER:
    # Subtract the remaining portion of this block
    remaining_dynamic -= (MAX_BLOCK - DEFHEADER)
    data_len += (MAX_BLOCK - DEFHEADER)
    # Subtract the next DEFLATE header
    remaining_dynamic -= DEFHEADER
    num_blocks += 1

  if remaining_dynamic <= 0:
    raise ValueError("Impossible to generate PNG of size " + str(size))

  data_len += remaining_dynamic
  width = data_len / PIXEL_LEN
  if (data_len % PIXEL_LEN) != 0:
    raise ValueError("Cannot generate image of size %d" % size)
  if (width < 0):
    raise ValueError("WTF " + str(size))
  return (width, height)

def factors(n):
  return list(set(reduce(list.__add__,
              ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0))))

def get_closest_factors(byte_length):
  # Choose the two factors that are closest in size to eachother
  all_factors = factors(byte_length)
  # prime the loop.
  x = all_factors.pop(0)
  y = byte_length / x
  current_distance = abs(x - y)
  for factor in all_factors:
    other_factor = (byte_length / factor)
    distance = abs(factor - other_factor)
    if distance < current_distance:
      x, y = factor, other_factor
      current_distance = distance
  return (x, y)

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print >> sys.stderr, "Usage: " + __file__ + " <# of bytes> <output file>"
    sys.exit(1)

  byte_length = int(sys.argv[1])
  output_file = sys.argv[2]

  (w, h) = get_dimensions(byte_length)
  img = generate_image_data(w,h)
  open(output_file, 'wb').write(to_png(w, h, img))
