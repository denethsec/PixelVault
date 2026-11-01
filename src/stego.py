"""Least-Significant-Bit (LSB) steganography for lossless images (PNG/BMP)."""
from PIL import Image, ImageChops

MAGIC = b"PVLT"          # marks images that contain a PixelVault message
LOSSLESS = {"PNG", "BMP"}


def _bits(data: bytes):
    for byte in data:
        for i in range(7, -1, -1):
            yield (byte >> i) & 1


def capacity_bytes(img: Image.Image) -> int:
    """Payload bytes available (3 bits per pixel, minus 8-byte header)."""
    return (img.width * img.height * 3) // 8 - 8


def encode(src: str, text: str, dst: str) -> int:
    """Hide text in src, save to dst (must be PNG/BMP). Returns bytes hidden."""
    if not dst.lower().endswith((".png", ".bmp")):
        raise ValueError("Output must be PNG or BMP: JPEG compression destroys hidden bits.")
    img = Image.open(src).convert("RGB")
    payload = text.encode("utf-8")
    if len(payload) > capacity_bytes(img):
        raise ValueError(f"Message too long: {len(payload)} bytes, capacity {capacity_bytes(img)}.")
    stream = list(_bits(MAGIC + len(payload).to_bytes(4, "big") + payload))
    flat = [c for px in img.getdata() for c in px]
    for i, bit in enumerate(stream):
        flat[i] = (flat[i] & ~1) | bit
    out = Image.new("RGB", img.size)
    out.putdata([tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)])
    out.save(dst)
    return len(payload)


def _read(flat, start_bit: int, n_bytes: int) -> bytes:
    out = bytearray()
    for b in range(n_bytes):
        v = 0
        for i in range(8):
            v = (v << 1) | (flat[start_bit + b * 8 + i] & 1)
        out.append(v)
    return bytes(out)


def decode(path: str) -> str:
    img = Image.open(path).convert("RGB")
    flat = [c for px in img.getdata() for c in px]
    if len(flat) < 64 or _read(flat, 0, 4) != MAGIC:
        raise ValueError("No PixelVault message found in this image.")
    length = int.from_bytes(_read(flat, 32, 4), "big")
    if length * 8 + 64 > len(flat):
        raise ValueError("Corrupted message length.")
    return _read(flat, 64, length).decode("utf-8")


def diff_stats(original: str, modified: str) -> dict:
    a, b = Image.open(original).convert("RGB"), Image.open(modified).convert("RGB")
    if a.size != b.size:
        raise ValueError("Images must be the same size.")
    pa, pb = list(a.getdata()), list(b.getdata())
    changed = sum(1 for x, y in zip(pa, pb) if x != y)
    max_delta = max((abs(c - d) for x, y in zip(pa, pb) for c, d in zip(x, y)), default=0)
    return {"pixels": len(pa), "pixels_changed": changed,
            "percent_changed": round(100 * changed / len(pa), 3), "max_channel_delta": max_delta}


def diff_image(original: str, modified: str, dst: str, amplify: int = 255) -> None:
    """Save a visual difference map: changed pixels are amplified so they are visible."""
    a, b = Image.open(original).convert("RGB"), Image.open(modified).convert("RGB")
    ImageChops.difference(a, b).point(lambda v: min(255, v * amplify)).save(dst)
