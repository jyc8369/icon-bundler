from pathlib import Path
import sys

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import (
    ICNS_SIZES,
    MissingSourceError,
    UnsupportedOutputFormatError,
    UnsupportedSourceError,
    build_icon_sizes,
    convert_image,
)


def write_png(path: Path, size: tuple[int, int] = (1024, 1024)) -> Path:
    Image.new("RGBA", size, (0, 128, 255, 255)).save(path)
    return path


def test_build_icon_sizes_includes_1024_for_large_icns_source() -> None:
    assert (1024, 1024) in build_icon_sizes((1024, 1024), ICNS_SIZES)


def test_build_icon_sizes_stops_before_upscaling() -> None:
    assert build_icon_sizes((32, 32), ICNS_SIZES) == [(16, 16), (32, 32)]


def test_convert_image_creates_ico_and_icns(tmp_path: Path) -> None:
    source = write_png(tmp_path / "icon.png")

    ico_path = convert_image(source, ".ico", "ICO")
    icns_path = convert_image(source, ".icns", "ICNS")

    assert ico_path.is_file()
    assert icns_path.is_file()


def test_convert_image_rejects_unsupported_source_extension(tmp_path: Path) -> None:
    source = tmp_path / "icon.gif"
    source.write_bytes(b"not an icon source")

    with pytest.raises(UnsupportedSourceError):
        convert_image(source, ".ico", "ICO")


def test_convert_image_rejects_missing_source(tmp_path: Path) -> None:
    with pytest.raises(MissingSourceError):
        convert_image(tmp_path / "missing.png", ".ico", "ICO")


def test_convert_image_rejects_format_suffix_mismatch(tmp_path: Path) -> None:
    source = write_png(tmp_path / "icon.png")

    with pytest.raises(UnsupportedOutputFormatError):
        convert_image(source, ".icns", "ICO")
