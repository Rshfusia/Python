"""Dataset loading, enrichment, sorting, filtering, and persistence for Lab 4."""

from __future__ import annotations

import os
from pathlib import Path

import cv2
import pandas as pd

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}
ABSOLUTE_COL = "absolute_path"
RELATIVE_COL = "relative_path"
LENGTH_COL = "image_length"


def _normalize_paths(raw_path: str, base_dir: Path) -> tuple[str, str]:
    """Convert a raw file path into (absolute_path, relative_path)."""
    candidate = Path(raw_path)
    abs_path = candidate.resolve() if candidate.is_absolute() else (base_dir / candidate).resolve()
    rel_path = Path(os.path.relpath(abs_path, start=base_dir.resolve())).as_posix()
    return str(abs_path), rel_path


def build_dataframe_from_annotation(
    annotation_path: Path,
    base_dir: Path | None = None,
) -> pd.DataFrame:
    """Build a named 2-column DataFrame from a Lab 2 CSV annotation file.

    :param annotation_path: Path to the CSV annotation file.
    :param base_dir: Base directory for computing relative paths.
    :return: DataFrame with columns ``absolute_path`` and ``relative_path``.
    """
    if not annotation_path.is_file():
        raise FileNotFoundError(f"Файл аннотации не найден: {annotation_path}")

    raw_df = pd.read_csv(annotation_path)
    if raw_df.empty:
        raise ValueError("Файл аннотации пуст.")

    root = (base_dir if base_dir is not None else annotation_path.parent).resolve()

    if ABSOLUTE_COL in raw_df.columns and RELATIVE_COL in raw_df.columns:
        df = raw_df[[ABSOLUTE_COL, RELATIVE_COL]].copy()
        df.columns = [ABSOLUTE_COL, RELATIVE_COL]
        return df

    path_candidates = [
        col
        for col in raw_df.columns
        if any(token in str(col).lower() for token in ("path", "file", "путь", "абс", "отн"))
    ]
    if len(path_candidates) >= 2:
        df = raw_df[[path_candidates[0], path_candidates[1]]].copy()
        df.columns = [ABSOLUTE_COL, RELATIVE_COL]
        return df

    source_col = path_candidates[0] if path_candidates else raw_df.columns[0]
    rows = [_normalize_paths(str(value), root) for value in raw_df[source_col].dropna()]
    df = pd.DataFrame(rows, columns=[ABSOLUTE_COL, RELATIVE_COL])
    return df


def build_dataframe_from_directory(
    images_dir: Path,
    base_dir: Path | None = None,
) -> pd.DataFrame:
    """Build a named 2-column DataFrame by scanning an image directory.

    :param images_dir: Directory containing image files.
    :param base_dir: Base directory for computing relative paths.
    :return: DataFrame with columns ``absolute_path`` and ``relative_path``.
    """
    if not images_dir.is_dir():
        raise FileNotFoundError(f"Папка с изображениями не найдена: {images_dir}")

    root = (base_dir if base_dir is not None else images_dir.parent).resolve()
    files = sorted(
        p
        for p in images_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )
    if not files:
        raise ValueError(f"В папке {images_dir} не найдено ни одного изображения.")

    rows = [_normalize_paths(str(file_path), root) for file_path in files]
    return pd.DataFrame(rows, columns=[ABSOLUTE_COL, RELATIVE_COL])


def get_image_length(image_path: Path) -> int:
    """Read an image file and return its length (height in pixels, ``shape[0]``).

    :param image_path: Path to the image file.
    :return: Image length in pixels.
    """
    if not image_path.is_file():
        raise FileNotFoundError(f"Изображение не найдено: {image_path}")
    image = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ValueError(f"Не удалось прочитать изображение: {image_path}")
    return int(image.shape[0])


def add_image_length_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add the ``image_length`` column containing the pixel length of each image.

    :param df: DataFrame containing ``absolute_path``.
    :return: Copy of DataFrame with the ``image_length`` column added.
    """
    if ABSOLUTE_COL not in df.columns:
        raise KeyError(f"В DataFrame отсутствует колонка '{ABSOLUTE_COL}'.")

    enriched = df.copy()
    enriched[LENGTH_COL] = [
        get_image_length(Path(str(path_value))) for path_value in enriched[ABSOLUTE_COL]
    ]
    return enriched


def sort_by_length(df: pd.DataFrame, *, ascending: bool = True) -> pd.DataFrame:
    """Sort DataFrame rows by the ``image_length`` column.

    :param df: DataFrame containing ``image_length``.
    :param ascending: Sort order (ascending if True, descending otherwise).
    :return: Sorted DataFrame with reset index.
    """
    if LENGTH_COL not in df.columns:
        raise KeyError(f"В DataFrame отсутствует колонка '{LENGTH_COL}'.")
    return df.sort_values(by=LENGTH_COL, ascending=ascending).reset_index(drop=True)


def filter_by_length(
    df: pd.DataFrame,
    *,
    min_length: int | None = None,
    max_length: int | None = None,
) -> pd.DataFrame:
    """Filter DataFrame rows by ``image_length`` bounds.

    :param df: DataFrame containing ``image_length``.
    :param min_length: Inclusive lower bound (optional).
    :param max_length: Inclusive upper bound (optional).
    :return: Filtered DataFrame with reset index.
    """
    if LENGTH_COL not in df.columns:
        raise KeyError(f"В DataFrame отсутствует колонка '{LENGTH_COL}'.")
    if min_length is not None and min_length < 0:
        raise ValueError(f"min_length должен быть >= 0, получено: {min_length}")
    if max_length is not None and max_length < 0:
        raise ValueError(f"max_length должен быть >= 0, получено: {max_length}")
    if min_length is not None and max_length is not None and min_length > max_length:
        raise ValueError(
            f"min_length ({min_length}) не может быть больше max_length ({max_length})."
        )

    mask = pd.Series(True, index=df.index)
    if min_length is not None:
        mask = mask & (df[LENGTH_COL] >= min_length)
    if max_length is not None:
        mask = mask & (df[LENGTH_COL] <= max_length)
    return df.loc[mask].reset_index(drop=True)


def save_dataframe(df: pd.DataFrame, output_path: Path) -> None:
    """Save a DataFrame to a CSV file.

    :param df: DataFrame to export.
    :param output_path: Destination CSV file path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
