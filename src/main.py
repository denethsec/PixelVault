import argparse
import sys

from . import stego


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="pixelvault", description="LSB image steganography lab.")
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("encode"); e.add_argument("image"); e.add_argument("message"); e.add_argument("-o", "--output", required=True)
    d = sub.add_parser("decode"); d.add_argument("image")
    c = sub.add_parser("compare"); c.add_argument("original"); c.add_argument("modified")
    c.add_argument("--diff-out", help="save an amplified difference image")
    k = sub.add_parser("capacity"); k.add_argument("image")
    a = p.parse_args(argv)
    try:
        if a.cmd == "encode":
            n = stego.encode(a.image, a.message, a.output); print(f"Hid {n} bytes in {a.output}")
        elif a.cmd == "decode":
            print(stego.decode(a.image))
        elif a.cmd == "compare":
            for k_, v in stego.diff_stats(a.original, a.modified).items(): print(f"{k_:>20}: {v}")
            if a.diff_out: stego.diff_image(a.original, a.modified, a.diff_out); print("Diff image:", a.diff_out)
        else:
            from PIL import Image
            print(stego.capacity_bytes(Image.open(a.image)), "bytes available")
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
