"""
This script serves as the main entry point for converting PDF and PNG files
containing tables into CSV format.

It accepts an input file path as a command-line argument and processes it
based on its extension. If a PDF file is provided, it is first converted into
a series of PNG images, one for each page. Each PNG image is then processed to
extract tabular data, which is subsequently written to a CSV file. If a PNG
file is provided, it is processed directly.

The script relies on three modules:
- `PDF2PNG`: To convert PDF files to PNG images.
- `recognition`: To extract tabular data from PNG images.
- `writeToCSV`: To write the extracted data to a CSV file.
"""
import argparse
import logging
from pathlib import Path

from PDF2PNG import convert_pdf2png
from recognition import parse_img_to_csv_data
from writeToCSV import write_csv

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract tabular data from a PDF or PNG file into CSV."
    )
    parser.add_argument("input_file", type=Path, help="Path to the input PDF or PNG file")
    args = parser.parse_args()

    input_file = args.input_file
    suffix = input_file.suffix.lower()

    if suffix == ".pdf":
        files = convert_pdf2png(input_file)
        for file in files:
            data = parse_img_to_csv_data(file)
            write_csv(file.with_suffix(".csv"), data)
    elif suffix == ".png":
        data = parse_img_to_csv_data(input_file)
        write_csv(input_file.with_suffix(".csv"), data)
    else:
        parser.error(f"Unsupported file format: {suffix or '(none)'}. Use PNG or PDF.")


if __name__ == "__main__":
    main()
