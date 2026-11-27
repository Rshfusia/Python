"""Image transformations for Lab 3 variant (1, 4, 10) using NumPy and OpenCV."""

from __future__ import annotations

import cv2
import numpy as np
from numpy.typing import NDArray

ImageArray = NDArray[np.uint8]


def crop_top_left(image: ImageArray, width: int, height: int) -> ImageArray:
    """Transform 1: Crop image from the top-left corner (0, 0) to (width, height)."""
    if width < 1 or height < 1:
        raise ValueError(f"Crop dimensions must be positive, got {width}x{height}.")
    if image.ndim < 2:
        raise ValueError(f"Expected 2D or 3D image array, got {image.ndim}D.")
    return image[:height, :width].copy()


def rotate_image(image: ImageArray, angle: float) -> ImageArray:
    """Transform 4: Rotate image counter-clockwise around its center by ``angle`` degrees."""
    if image.ndim < 2:
        raise ValueError(f"Expected 2D or 3D image array, got {image.ndim}D.")
    if angle % 360.0 == 0.0:
        return image.copy()

    img_h, img_w = image.shape[:2]
    center = (img_w / 2.0, img_h / 2.0)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated: ImageArray = np.asarray(
        cv2.warpAffine(image, matrix, (img_w, img_h)),
        dtype=np.uint8,
    )
    return rotated


def _match_channels(image: ImageArray, target_channels: int) -> ImageArray:
    """Convert grayscale/BGRA image to match target channel count (1 or 3)."""
    current_channels = 1 if image.ndim == 2 else image.shape[2]
    if current_channels == target_channels:
        return image
    if target_channels == 3 and current_channels == 1:
        return np.asarray(cv2.cvtColor(image, cv2.COLOR_GRAY2BGR), dtype=np.uint8)
    if target_channels == 3 and current_channels == 4:
        return np.asarray(cv2.cvtColor(image, cv2.COLOR_BGRA2BGR), dtype=np.uint8)
    if target_channels == 1 and current_channels == 3:
        return np.asarray(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), dtype=np.uint8)
    if target_channels == 1 and current_channels == 4:
        return np.asarray(cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY), dtype=np.uint8)
    raise ValueError(f"Unsupported channel conversion: {current_channels} -> {target_channels}.")


def overlay_translucent(
    base: ImageArray,
    overlay: ImageArray,
    alpha: float = 0.5,
    offset_x: int = 0,
    offset_y: int = 0,
) -> ImageArray:
    """Transform 10: Overlay ``overlay`` onto ``base`` with transparency ``alpha`` in [0, 1]."""
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha must be in [0.0, 1.0], got {alpha}.")
    if offset_x < 0 or offset_y < 0:
        raise ValueError(f"Offsets must be non-negative, got ({offset_x}, {offset_y}).")

    result = base.copy()
    base_h, base_w = result.shape[:2]
    ov_h, ov_w = overlay.shape[:2]

    end_y = min(base_h, offset_y + ov_h)
    end_x = min(base_w, offset_x + ov_w)
    if end_y <= offset_y or end_x <= offset_x:
        return result

    roi_h = end_y - offset_y
    roi_w = end_x - offset_x

    base_channels = 1 if result.ndim == 2 else result.shape[2]
    aligned_overlay = _match_channels(overlay[:roi_h, :roi_w], base_channels)

    base_roi = result[offset_y:end_y, offset_x:end_x]
    blended = cv2.addWeighted(base_roi, 1.0 - alpha, aligned_overlay, alpha, 0.0)
    result[offset_y:end_y, offset_x:end_x] = blended
    return result


def apply_pipeline(
    image: ImageArray,
    overlay: ImageArray,
    *,
    width: int,
    height: int,
    angle: float,
    alpha: float = 0.5,
) -> ImageArray:
    """Apply Lab 3 variant (1, 4, 10) transformations sequentially."""
    cropped = crop_top_left(image, width=width, height=height)
    rotated = rotate_image(cropped, angle=angle)
    return overlay_translucent(rotated, overlay, alpha=alpha)
