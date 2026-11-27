"""CLI entry point for Lab 4: build DataFrame, add image length, sort, filter, plot, save."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from lab4.dataset import (
    add_image_length_column,
    build_dataframe_from_annotation,
    build_dataframe_from_directory,
    filter_by_length,
    save_dataframe,
    sort_by_length,
)
from lab4.visualization import plot_length_histogram


def build_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser for Lab 4.

    :return: Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="lab4",
        description="Лабораторная работа №4 (вариант 1): анализ длины изображений и гистограмма.",
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--annotation",
        type=Path,
        help="Путь к CSV-аннотации из 2-й лабораторной работы.",
    )
    source_group.add_argument(
        "--images-dir",
        type=Path,
        help="Путь к папке с изображениями (если нет CSV-аннотации).",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=None,
        help="Базовая папка для расчёта относительных путей.",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("output/dataset_sorted.csv"),
        help="Путь для сохранения итогового DataFrame в CSV.",
    )
    parser.add_argument(
        "--output-plot",
        type=Path,
        default=Path("output/length_histogram.png"),
        help="Путь для сохранения графика гистограммы.",
    )
    parser.add_argument("--min-length", type=int, default=None, help="Минимальная длина (фильтр).")
    parser.add_argument("--max-length", type=int, default=None, help="Максимальная длина (фильтр).")
    parser.add_argument(
        "--descending",
        action="store_true",
        help="Сортировать по убыванию длины.",
    )
    parser.add_argument("--bins", type=int, default=10, help="Количество столбцов гистограммы.")
    parser.add_argument("--no-show", action="store_true", help="Не открывать окно matplotlib.")
    return parser


def run_cli(argv: Sequence[str] | None = None) -> int:
    """Execute the Lab 4 data analysis and visualization pipeline.

    :param argv: Optional list of CLI arguments.
    :return: Exit code (0 on success).
    """
    args = build_parser().parse_args(list(argv) if argv is not None else None)

    if args.annotation is not None:
        df = build_dataframe_from_annotation(args.annotation, base_dir=args.base_dir)
    else:
        df = build_dataframe_from_directory(args.images_dir, base_dir=args.base_dir)

    enriched_df = add_image_length_column(df)
    sorted_df = sort_by_length(enriched_df, ascending=not bool(args.descending))
    filtered_df = filter_by_length(
        sorted_df,
        min_length=args.min_length,
        max_length=args.max_length,
    )

    print("Отсортированный DataFrame:")
    print(sorted_df.to_string(index=False))
    print(f"\nПосле фильтрации осталось записей: {len(filtered_df)}")

    save_dataframe(sorted_df, args.output_csv)
    plot_length_histogram(
        sorted_df,
        output_path=args.output_plot,
        bins=int(args.bins),
        show=not bool(args.no_show),
    )
    return 0


def main() -> None:
    """CLI entry point with explicit exception handling."""
    try:
        run_cli()
    except (FileNotFoundError, ValueError, KeyError, OSError) as exc:
        print(f"Ошибка: {exc}")


if __name__ == "__main__":
    main()
