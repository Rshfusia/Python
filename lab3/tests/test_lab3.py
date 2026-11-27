"""Tests for Lab 3: image transformations (1, 4, 10) and CLI."""

from __future__ import annotations

from pathlib import Path

import cv2
import matplotlib
import numpy as np
import pytest

from lab3.main import run_cli
from lab3.transforms import (
    ImageArray,
    apply_pipeline,
    crop_top_left,
    overlay_translucent,
    rotate_image,
)


@pytest.fixture(autouse=True)
def _headless_matplotlib() -> None:
    """Configure non-interactive matplotlib backend for tests."""
    matplotlib.use("Agg")


def _make_quadrant_image(width: int = 100, height: int = 80) -> ImageArray:
    """Create a synthetic BGR test image with colored quadrants."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[: height // 2, : width // 2] = (0, 0, 255)
    img[: height // 2, width // 2 :] = (0, 255, 0)
    img[height // 2 :, :] = (255, 0, 0)
    return img


def test_crop_top_left() -> None:
    """Verify top-left cropping and dimension validation."""
    img = _make_quadrant_image(100, 80)
    cropped = crop_top_left(img, width=40, height=30)
    assert cropped.shape == (30, 40, 3)
    assert tuple(int(v) for v in cropped[0, 0]) == (0, 0, 255)
    assert tuple(int(v) for v in cropped[29, 39]) == (0, 0, 255)

    clamped = crop_top_left(img, width=200, height=150)
    assert clamped.shape == (80, 100, 3)

    with pytest.raises(ValueError):
        crop_top_left(img, width=0, height=10)


def test_rotate_image() -> None:
    """Verify rotation preserves shape and transforms pixels."""
    img = _make_quadrant_image(60, 60)
    same = rotate_image(img, 0.0)
    assert np.array_equal(same, img)

    rotated = rotate_image(img, 90.0)
    assert rotated.shape == img.shape
    assert not np.array_equal(rotated, img)


def test_overlay_translucent() -> None:
    """Verify translucent alpha blending and alpha bounds validation."""
    base = np.full((40, 50, 3), 100, dtype=np.uint8)
    overlay = np.full((20, 30, 3), 200, dtype=np.uint8)

    blended = overlay_translucent(base, overlay, alpha=0.5)
    assert blended.shape == base.shape
    assert int(blended[0, 0, 0]) == 150
    assert int(blended[30, 40, 0]) == 100

    with pytest.raises(ValueError, match="alpha"):
        overlay_translucent(base, overlay, alpha=1.5)


def test_apply_pipeline_and_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verify full CLI pipeline reads, transforms, prints sizes, and saves output."""
    src_path = tmp_path / "source.png"
    ov_path = tmp_path / "overlay.png"
    out_path = tmp_path / "out" / "result.png"

    src_img = _make_quadrant_image(120, 100)
    ov_img = np.full((50, 60, 3), 255, dtype=np.uint8)

    assert cv2.imwrite(str(src_path), src_img)
    assert cv2.imwrite(str(ov_path), ov_img)

    code = run_cli(
        [
            "--input",
            str(src_path),
            "--overlay",
            str(ov_path),
            "--output",
            str(out_path),
            "--width",
            "80",
            "--height",
            "60",
            "--angle",
            "30",
            "--alpha",
            "0.4",
            "--no-show",
        ]
    )
    assert code == 0
    assert out_path.is_file()

    stdout = capsys.readouterr().out
    assert "120x100" in stdout
    assert "80x60" in stdout

    saved = cv2.imread(str(out_path))
    assert saved is not None
    assert saved.shape == (60, 80, 3)

    piped = apply_pipeline(src_img, ov_img, width=80, height=60, angle=30, alpha=0.4)
    assert piped.shape == (60, 80, 3)


def test_cli_missing_input_raises(tmp_path: Path) -> None:
    """Verify missing input file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        run_cli(
            [
                "--input",
                str(tmp_path / "missing.png"),
                "--overlay",
                str(tmp_path / "ov.png"),
                "--output",
                str(tmp_path / "out.png"),
                "--width",
                "10",
                "--height",
                "10",
                "--angle",
                "0",
                "--no-show",
            ]
        )
