import pytest
from PIL import Image
from src import stego


@pytest.fixture
def cover(tmp_path):
    p = tmp_path / "cover.png"
    Image.effect_noise((64, 64), 40).convert("RGB").save(p)
    return str(p)


def test_round_trip(cover, tmp_path):
    out = str(tmp_path / "s.png")
    stego.encode(cover, "Hello, café ☕", out)
    assert stego.decode(out) == "Hello, café ☕"


def test_change_is_invisible(cover, tmp_path):
    out = str(tmp_path / "s.png"); stego.encode(cover, "secret message", out)
    assert stego.diff_stats(cover, out)["max_channel_delta"] <= 1


def test_clean_image_has_no_message(cover):
    with pytest.raises(ValueError):
        stego.decode(cover)


def test_too_long_and_jpeg_rejected(cover, tmp_path):
    with pytest.raises(ValueError):
        stego.encode(cover, "x" * 5000, str(tmp_path / "a.png"))
    with pytest.raises(ValueError):
        stego.encode(cover, "hi", str(tmp_path / "a.jpg"))
