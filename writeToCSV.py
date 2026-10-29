"""
This module provides a function for writing data to a CSV file.

It takes a file path and a list of lists, and writes the data to the specified
CSV file.
"""
import csv
import logging
import io
import re
from pathlib import Path

from output_files import publish_bytes

logger = logging.getLogger(__name__)


def write_csv(path: Path, data) -> None:
    """Writes a list of lists to a CSV file.

    This function takes a file path and a list of lists, and writes the data
    to a CSV file. Each inner list is written as a row in the CSV file.

    Args:
        path: The file path for the output CSV file.
        data: A list of lists representing the data to be written.
    """
    file_path = path if path.is_absolute() else Path.cwd() / path

    # cp1251 matches the encoding Russian-locale Excel expects when opening
    # this CSV directly, rather than utf-8.
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, dialect="excel")
    for item in data:
        safe_row = []
        for value in item:
            if isinstance(value, str):
                stripped = value.lstrip()
                numeric_negative = re.fullmatch(r"-\d+(?:[.,]\d+)?(?:[eE][+-]?\d+)?", stripped)
                if stripped.startswith(("=", "+", "@")) or (stripped.startswith("-") and not numeric_negative):
                    value = "'" + value
            safe_row.append(value)
        writer.writerow(safe_row)
    # Encode before touching the destination: unsupported Unicode leaves no partial CSV.
    publish_bytes(file_path, buffer.getvalue().encode("cp1251"))
    logger.info("File written: %s - done!\n", file_path.name)
    logger.info("#" * 66)
