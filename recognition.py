"""
This module provides functions for recognizing and extracting tabular data from
images.

It uses computer vision techniques to identify the cell coordinates of a table
in an image, extracts the text from each cell using optical character
recognition (OCR), and returns the data in a structured format.
"""

import os
import re
from pathlib import Path

import cv2 as cv
import numpy as np
import pytesseract

# On Windows, Tesseract usually isn't on PATH by default. Set TESSERACT_CMD
# to its full path (e.g. C:\Program Files\Tesseract-OCR\tesseract.exe) if
# `tesseract` isn't already resolvable on PATH. On macOS/Linux, installing
# via a package manager (brew/apt) normally puts it on PATH already, so this
# is left unset there.
if "TESSERACT_CMD" in os.environ:
    pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]


def _grid_coordinates(points: np.ndarray) -> list[int]:
    """Keep the last pixel in each cluster of adjacent grid intersections."""
    sorted_points = np.sort(points)
    if len(sorted_points) == 0:
        return []
    coordinates = [
        int(sorted_points[i])
        for i in range(len(sorted_points) - 1)
        if sorted_points[i + 1] - sorted_points[i] > 10
    ]
    coordinates.append(int(sorted_points[-1]))
    return coordinates


def parse_img_to_csv_data(src: Path):
    """Extracts tabular data from an image.

    This function processes an image to identify a table structure, extracts
    the text from each cell using OCR, and returns the data as a list of lists.

    The process involves the following steps:
    1.  Convert the image to grayscale and then to a binary format.
    2.  Detect horizontal and vertical lines to identify the table structure.
    3.  Find the intersection points of the lines to determine the cell
        coordinates.
    4.  Extract the content of each cell and convert it to text using OCR.
    5.  Clean the extracted text by removing special characters.

    Args:
        src: The file path of the input image.

    Returns:
        A list of lists representing the tabular data, where each inner list
        corresponds to a row in the table.
    """
    raw = cv.imread(str(src), 1)
    if raw is None:
        raise ValueError(f"Could not read image: {src}")

    # Grayscale image
    gray = cv.cvtColor(raw, cv.COLOR_BGR2GRAY)

    # Binarization
    binary = cv.adaptiveThreshold(~gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 35, -5)  # tune the fifth parameter, e.g. 21
    rows, cols = binary.shape

    # Detect horizontal lines
    scale = 40  # can be set anywhere from 20-60
    mask = cv.getStructuringElement(cv.MORPH_RECT, (max(1, cols // scale), 1))
    eroded = cv.erode(binary, mask, iterations=1)
    dilated_col = cv.dilate(eroded, mask, iterations=1)

    # Detect vertical lines
    scale = 20  # can be set anywhere from 10-30
    mask = cv.getStructuringElement(cv.MORPH_RECT, (1, max(1, rows // scale)))
    eroded = cv.erode(binary, mask, iterations=1)
    dilated_row = cv.dilate(eroded, mask, iterations=1)

    # Detect intersections
    bitwise_and = cv.bitwise_and(dilated_col, dilated_row)  # bitwise AND is true only where both pixels are nonzero

    # Find white intersections on the black-and-white image and derive the
    # horizontal and vertical coordinates.
    y_point, x_point = np.where(bitwise_and > 0)
    # Sorting yields the x/y transition values that mark an intersection
    # point; otherwise an intersection point would produce many pixel
    # values close together. Only the last point of each similar-value
    # cluster is kept.
    # This gap of 10 is not fixed -- it should be tuned per image. It's
    # essentially the cell height (y-coordinate gap) and length
    # (x-coordinate gap) of the table.
    x_point_arr = _grid_coordinates(x_point)
    y_point_arr = _grid_coordinates(y_point)
    if len(x_point_arr) < 2 or len(y_point_arr) < 2:
        raise ValueError(f"No table grid detected in image: {src}")

    # Loop over the table, splitting by y-coordinates and x-coordinates
    data = [[] for _ in range(len(y_point_arr) - 1)]
    for i in range(len(y_point_arr) - 1):
        for j in range(len(x_point_arr) - 1):

            # When slicing, the first parameter is the y-coordinate, the second is the x-coordinate
            cell = raw[y_point_arr[i]:y_point_arr[i + 1], x_point_arr[j]:x_point_arr[j + 1]]

            # Read the text out of the cell
            text = pytesseract.image_to_string(cell, lang="rus")

            # Strip special characters
            text = re.findall(r'[^\*"$@&/?\\|<>~`″′‖{}!#〈\n]', text, re.S)
            text = "".join(text)
            data[i].append(text)
            j = j + 1
        i = i + 1

    return data
