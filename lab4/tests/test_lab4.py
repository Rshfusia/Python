"""Tests for Lab 4: DataFrame construction, length column, sorting, filtering, and histogram."""

from __future__ import annotations

from pathlib import Path

import cv2
import matplotlib
import numpy as np
import pandas as pd
import pytest

from lab4.dataset import (
    ABSOLUTE_COL,
    LENGTH_COL,
    RELATIVE_COL,
    add_image_length_column,
    build_dataframe_from_annotation,
    build_dataframe_from_directory,
    filter_by_length,
    save_dataframe,
    sort_by_length,
)
from lab4.main import run_cli
from lab4.visualization import plot_length_histogram


@pytest.fixture(autouse=True)
def _headless_matplotlib() -> None:
    """Configure non-interactive matplotlib backend for tests."""
    matplotlib.use("Agg")


def _write_test_image(path: Path, width: int, height: int) -> None:
    """Create a solid BGR PNG image with specified dimensions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    img = np.zeros((height, width, 3), dtype=np.uint8)
    assert cv2.imwrite(str(path), img)


def test_build_dataframe_enrich_sort_and_filter(tmp_path: Path) -> None:
    """Verify DataFrame creation from CSV annotation, length calculation, sort, and filter."""
    img_dir = tmp_path / "images"
    _write_test_image(img_dir / "a.png", width=50, height=120)
    _write_test_image(img_dir / "b.png", width=60, height=40)
    _write_test_image(img_dir / "c.png", width=70, height=80)

    annotation = tmp_path / "annotations.csv"
    pd.DataFrame({"filepath": ["images/a.png", "images/b.png", "images/c.png"]}).to_csv(
        annotation,
        index=False,
    )

    df = build_dataframe_from_annotation(annotation)
    assert list(df.columns) == [ABSOLUTE_COL, RELATIVE_COL]
    assert len(df) == 3

    enriched = add_image_length_column(df)
    assert list(enriched[LENGTH_COL]) == [120, 40, 80]

    sorted_asc = sort_by_length(enriched, ascending=True)
    assert list(sorted_asc[LENGTH_COL]) == [40, 80, 120]

    sorted_desc = sort_by_length(enriched, ascending=False)
    assert list(sorted_desc[LENGTH_COL]) == [120, 80, 40]

    filtered = filter_by_length(sorted_asc, min_length=50, max_length=100)
    assert list(filtered[LENGTH_COL]) == [80]


def test_build_from_directory_and_save_plot(tmp_path: Path) -> None:
    """Verify directory scan, CSV save, and histogram PNG generation."""
    img_dir = tmp_path / "dataset"
    _write_test_image(img_dir / "one.png", width=30, height=60)
    _write_test_image(img_dir / "two.png", width=30, height=90)

    df = build_dataframe_from_directory(img_dir, base_dir=tmp_path)
    enriched = sort_by_length(add_image_length_column(df))

    out_csv = tmp_path / "out" / "data.csv"
    out_plot = tmp_path / "out" / "hist.png"

    save_dataframe(enriched, out_csv)
    plot_length_histogram(enriched, output_path=out_plot, bins=5, show=False)

    assert out_csv.is_file()
    assert out_plot.is_file()
    reloaded = pd.read_csv(out_csv)
    assert list(reloaded[LENGTH_COL]) == [60, 90]


def test_cli_end_to_end_and_validation(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verify CLI execution and validation errors."""
    img_dir = tmp_path / "imgs"
    _write_test_image(img_dir / "x.png", width=20, height=55)
    _write_test_image(img_dir / "y.png", width=20, height=110)

    out_csv = tmp_path / "res.csv"
    out_plot = tmp_path / "res.png"

    code = run_cli(
        [
            "--images-dir",
            str(img_dir),
            "--output-csv",
            str(out_csv),
            "--output-plot",
            str(out_plot),
            "--min-length",
            "60",
            "--no-show",
        ]
    )
    assert code == 0
    assert out_csv.is_file()
    assert out_plot.is_file()
    output = capsys.readouterr().out
    assert "image_length" in output
    assert "осталось записей: 1" in output

    with pytest.raises(ValueError, match="min_length"):
        filter_by_length(pd.DataFrame({LENGTH_COL: [10]}), min_length=50, max_length=10)

    with pytest.raises(FileNotFoundError):
        build_dataframe_from_annotation(tmp_path / "missing.csv")
