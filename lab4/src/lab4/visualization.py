"""Histogram visualization for Lab 4 using matplotlib."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from lab4.dataset import LENGTH_COL


def plot_length_histogram(
    sorted_df: pd.DataFrame,
    output_path: Path | None = None,
    *,
    bins: int = 10,
    show: bool = True,
) -> None:
    """Plot and optionally save a histogram of ``image_length`` for all sorted data.

    :param sorted_df: Sorted DataFrame containing ``image_length``.
    :param output_path: Optional file path to save the figure.
    :param bins: Number of histogram bins (must be >= 1).
    :param show: Whether to display the matplotlib window.
    """
    if LENGTH_COL not in sorted_df.columns:
        raise KeyError(f"В DataFrame отсутствует колонка '{LENGTH_COL}'.")
    if sorted_df.empty:
        raise ValueError("Невозможно построить гистограмму для пустого DataFrame.")
    if bins < 1:
        raise ValueError(f"Количество интервалов (bins) должно быть >= 1, получено: {bins}")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(sorted_df[LENGTH_COL], bins=bins, color="#3b82f6", edgecolor="black")
    ax.set_title("Распределение длины изображений (все отсортированные данные)")
    ax.set_xlabel("Длина изображения (пиксели)")
    ax.set_ylabel("Количество изображений")
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    fig.tight_layout()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150)

    if show:
        plt.show()
    else:
        plt.close(fig)
