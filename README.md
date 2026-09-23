# Recognition of Russian Financial Reports (Tesseract OCR)

Tesseract-based OCR extraction of tabular data from Russian-language financial
report PDFs and PNGs, converted to CSV. The script uses computer vision to
locate the table's cell boundaries, then reads each cell with Tesseract OCR.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)
- [How It Works](#how-it-works)
- [Dependencies](#dependencies)
- [Disclaimer](#disclaimer)

## Getting Started

Follow these instructions to set up and run the script on your local machine.

### Prerequisites

- Python 3.9+
- Tesseract OCR Engine, with the Russian (`rus`) language pack installed

Install Tesseract via your platform's package manager (`brew install tesseract tesseract-lang` on macOS, `apt install tesseract-ocr tesseract-ocr-rus` on Debian/Ubuntu) or from the [official repository](https://github.com/tesseract-ocr/tesseract). If `tesseract` isn't on your `PATH` after installing (this is common on Windows), set the `TESSERACT_CMD` environment variable to its full path, e.g.:

```sh
# Windows PowerShell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### Installation

```sh
git clone https://github.com/denis-samatov/recognition-russian-financial-reports.git
cd recognition-russian-financial-reports
pip install -e .
```

### Usage

Run the `pdf2csv` command with the path to a PDF or PNG file:

```sh
pdf2csv path/to/report.pdf
```

For a PNG, the script writes a CSV next to the input. For a PDF, it writes one
CSV per page alongside the rendered pages in `table in PNG/` under the current
working directory. An unreadable image or an image without a detectable table
grid raises an error; the CSV should always be checked against the source.

## How It Works

The script processes the input file in the following steps:

1.  **File Handling:**
    - If the input file is a PDF, it is converted into a series of PNG images, one for each page.
    - If the input file is a PNG, it is processed directly.

2.  **Image Processing:**
    - The image is converted to grayscale and then to a binary format to improve the accuracy of text recognition.
    - The script identifies the horizontal and vertical lines of the table to determine the cell coordinates.

    <div align="center">
        <img src="https://github.com/denis-samatov/recognition-russian-financial-reports/blob/main/image_1.png" alt="Table Image">
    </div>

3.  **Data Extraction:**
    - The content of each cell is extracted using the calculated coordinates.
    - The text from each cell is recognized using the Tesseract OCR engine.

    <div align="center">
        <img src="https://github.com/denis-samatov/recognition-russian-financial-reports/blob/main/image_2.png" alt="Horizontal Table Lines">
        <img src="https://github.com/denis-samatov/recognition-russian-financial-reports/blob/main/image_3.png" alt="Vertical Table Lines">
    </div>

4.  **CSV Generation:**
    - The extracted data is written to a CSV file (encoded `cp1251`, so it opens correctly in Russian-locale Excel).

## Dependencies

This script relies on the following Python libraries, declared in `pyproject.toml`:

-   **PyMuPDF (`fitz`)**: For converting PDF files to PNG images.
-   **OpenCV-Python (`cv2`)**: For image processing and table detection.
-   **NumPy**: For numerical operations and handling image data.
-   **Pytesseract**: For optical character recognition (OCR).

`pip install -e .` installs all of them.

## Tests

```sh
pip install -e '.[dev]'
pytest -q
ruff check .
```

The tests use generated images and replace the OCR call. They check input
errors and table row structure, not Tesseract recognition quality.

## Disclaimer

This script is provided "as is." The results may vary depending on the nature and complexity of the tables in the input files. It is recommended to carefully review the generated CSV files for accuracy before using them. No neural network is trained or used anywhere in this pipeline — table structure is found with classical computer-vision line detection, and text is read with Tesseract's OCR engine.
