#!/usr/bin/env python3
"""THE WORLD — V3.2 entry loader (pure standard library).

Reads entry.png from the directory this file lives in, validates it, and
writes its exact bytes to the output path given as the first command-line
argument (or to stdout when no path is given).

Validation before anything is written:
  * file smaller than 1 MiB
  * PNG signature
  * IHDR is the first chunk: 1024x1024, bit depth 8, colour type 2 (RGB)
  * every chunk's CRC matches its type + data
  * the concatenated IDAT payload decompresses to exactly one full RGB
    frame (height * (1 + width * 3) bytes)
  * an IEND chunk is present

Exit 0 on success. Exit 1 with a message on stderr on any failure.
"""

import os
import struct
import sys
import zlib

SIG = b"\x89PNG\r\n\x1a\n"
LIMIT = 1_048_576
W, H = 1024, 1024
DEPTH, CTYPE = 8, 2


def die(msg):
    sys.stderr.write("error: %s\n" % msg)
    sys.exit(1)


def run(argv):
    base = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(base, "entry.png")
    try:
        with open(src, "rb") as fh:
            blob = fh.read()
    except OSError as exc:
        die("cannot read entry.png: %s" % exc)

    if len(blob) > LIMIT:
        die("entry.png is %d bytes, over the 1 MiB limit" % len(blob))
    if blob[:8] != SIG:
        die("not a PNG file (bad signature)")

    pos = 8
    got_ihdr = got_iend = False
    idat = bytearray()
    while pos + 8 <= len(blob):
        (n,) = struct.unpack(">I", blob[pos:pos + 4])
        typ = blob[pos + 4:pos + 8]
        end = pos + 8 + n + 4
        if end > len(blob):
            die("truncated %s chunk" % typ.decode("latin-1", "replace"))
        data = blob[pos + 8:pos + 8 + n]
        (want,) = struct.unpack(">I", blob[pos + 8 + n:end])
        if zlib.crc32(typ + data) & 0xFFFFFFFF != want:
            die("chunk %r CRC mismatch" % typ.decode("latin-1", "replace"))
        if not got_ihdr:
            if typ != b"IHDR":
                die("first chunk is %r, expected IHDR"
                    % typ.decode("latin-1", "replace"))
            if n != 13:
                die("IHDR length is %d, expected 13" % n)
            w, h, depth, ct = struct.unpack(">IIBB", data[:10])
            if (w, h) != (W, H):
                die("expected 1024x1024, got %dx%d" % (w, h))
            if depth != DEPTH or ct != CTYPE:
                die("expected 8-bit RGB, got depth %d type %d"
                    % (depth, ct))
            got_ihdr = True
        elif typ == b"IDAT":
            idat += data
        elif typ == b"IEND":
            got_iend = True
            break
        pos = end

    if not got_ihdr:
        die("no IHDR chunk found")
    if not got_iend:
        die("no IEND chunk found")
    if not idat:
        die("no IDAT data found")
    try:
        raw = zlib.decompress(bytes(idat))
    except zlib.error as exc:
        die("IDAT does not decompress: %s" % exc)
    if len(raw) != H * (1 + W * 3):
        die("decompressed IDAT is %d bytes, expected %d"
            % (len(raw), H * (1 + W * 3)))

    if len(argv) > 1:
        try:
            with open(argv[1], "wb") as fh:
                fh.write(blob)
        except OSError as exc:
            die("cannot write output: %s" % exc)
    else:
        try:
            sys.stdout.buffer.write(blob)
        except OSError as exc:
            die("cannot write output: %s" % exc)
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv))
