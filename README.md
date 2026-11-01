# PixelVault — Image Steganography Lab

An educational lab showing how information can hide inside an image by changing the least significant bit (LSB) of each colour channel. Each change shifts a channel value by at most 1 out of 255, which is invisible to the eye.

## Features
- Encode UTF-8 text into PNG/BMP images
- Decode messages (a `PVLT` header marks images that carry one)
- Capacity check before encoding
- Compare original vs modified: pixels changed, max channel difference
- Amplified difference image so you can *see* where data was hidden

## Installation
```bash
git clone https://github.com/<you>/PixelVault.git && cd PixelVault
pip install -r requirements.txt
```

## How to run
```bash
python -m src.main capacity photo.png
python -m src.main encode photo.png "Meet at noon" -o secret.png
python -m src.main decode secret.png
python -m src.main compare photo.png secret.png --diff-out diff.png
```

## Example output
```
$ python -m src.main compare photo.png secret.png
              pixels: 786432
     pixels_changed: 9
    percent_changed: 0.001
  max_channel_delta: 1
```
Put the original, `secret.png` and `diff.png` side by side in `screenshots/`.

## Limitations
- Lossless formats only; saving as JPEG or resizing destroys the message.
- The message is **not encrypted**; anyone who knows the method can read it. Encrypt first for real secrecy.
- Plain sequential LSB is easy to detect with statistical analysis (a good topic to extend into).

## Tests
```bash
pytest
```

## Technologies
Python 3 · Pillow · bitwise operations

## License
MIT
