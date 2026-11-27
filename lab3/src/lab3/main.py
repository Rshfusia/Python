"""CLI entry point for Lab 3: read image, print size, transform (1, 4, 10), plot, save."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np

from lab3.transforms import ImageArray, apply_pipeline


def load_image(path: Path) -> ImageArray:
    """Load a BGR image from disk using OpenCV.

    :param path: Path to the source image file.
    :return: Image array with uint8 BGR pixels.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Файл изображения не найден: {path}")
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Не удалось декодировать изображение: {path}")
    return np.asarray(image, dtype=np.uint8)


def to_rgb(image: ImageArray) -> ImageArray:
    """Convert a BGR OpenCV image array to RGB for matplotlib display.

    :param image: Source BGR or grayscale image array.
    :return: RGB image array.
    """
    if image.ndim == 2:
        return image
    return np.asarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), dtype=np.uint8)


def show_comparison(original: ImageArray, result: ImageArray, *, show: bool = True) -> None:
    """Display original and transformed images side-by-side using matplotlib.

    :param original: Original BGR image array.
    :param result: Transformed BGR image array.
    :param show: Whether to open the matplotlib window.
    """
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(to_rgb(original))
    axes[0].set_title(f"Исходное ({original.shape[1]}x{original.shape[0]})")
    axes[0].axis("off")

    axes[1].imshow(to_rgb(result))
    axes[1].set_title(f"Результат ({result.shape[1]}x{result.shape[0]})")
    axes[1].axis("off")

    fig.tight_layout()
    if show:
        plt.show()
    else:
        plt.close(fig)


def build_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser for Lab 3.

    :return: Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="lab3",
        description="Лабораторная работа №3 (вариант 1, 4, 10): обрезка, поворот, наложение.",
    )
    parser.add_argument("--input", required=True, type=Path, help="Путь к исходному изображению.")
    parser.add_argument("--output", required=True, type=Path, help="Путь для сохранения.")
    parser.add_argument("--overlay", required=True, type=Path, help="Путь к накладываемому фото.")
    parser.add_argument("--width", required=True, type=int, help="Ширина обрезки (преобр. 1).")
    parser.add_argument("--height", required=True, type=int, help="Высота обрезки (преобр. 1).")
    parser.add_argument("--angle", required=True, type=float, help="Угол поворота (преобр. 4).")
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.5,
        help="Прозрачность наложения от 0.0 до 1.0 (преобр. 10).",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Не открывать окно matplotlib.",
    )
    return parser


def run_cli(argv: Sequence[str] | None = None) -> int:
    """Execute the Lab 3 pipeline for given CLI arguments.

    :param argv: Optional argument list (defaults to sys.argv).
    :return: Exit status code (0 on success).
    """
    args = build_parser().parse_args(list(argv) if argv is not None else None)

    original = load_image(args.input)
    overlay = load_image(args.overlay)

    height, width, channels = original.shape
    print(f"Размер исходного изображения: {width}x{height}, каналов: {channels}")

    result = apply_pipeline(
        original,
        overlay,
        width=int(args.width),
        height=int(args.height),
        angle=float(args.angle),
        alpha=float(args.alpha),
    )

    res_h, res_w, res_c = result.shape
    print(f"Размер результата: {res_w}x{res_h}, каналов: {res_c}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(args.output), result):
        raise OSError(f"Не удалось сохранить результат в файл: {args.output}")

    show_comparison(original, result, show=not bool(args.no_show))
    return 0


def main() -> None:
    """CLI entry point with explicit exception handling."""
    try:
        run_cli()
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"Ошибка: {exc}")


if __name__ == "__main__":
    main()
