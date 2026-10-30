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

- Python 3.13 for the maintained validated execution profile (package metadata retains a historical Python 3.9 minimum; that entire version range is not qualified)
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
python -m pip install --require-hashes -r requirements-execution.txt
python -m pip install --no-deps --no-build-isolation .
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

## Safe output contract

Existing PNG/CSV destinations are never replaced. Each individual output is fully serialized before an atomic no-clobber publish; a failure leaves no partially published file. A PDF may still leave successfully completed earlier pages if a later page fails: inspect the reported error and use a fresh output directory rather than assuming document-level all-or-nothing completion. Select a separate location for same-basename inputs with `pdf2csv input/report.pdf --output-dir results/report-one`.

CSV remains cp1251 for compatibility. An unencodable character raises UnicodeEncodeError before creating a destination; the source document is never changed. Formula-like cells beginning with =,+,@ or a nonnumeric minus expression are prefixed with an apostrophe for spreadsheet consumption. Ordinary negative numbers such as -3.5/-1,25 remain numeric text. The input PDF/PNG remains the original evidence; cell text is recognized OCR output, not ground truth; CSV text escaping is a presentation policy, not a numerical correction.

`tests/test_outputs.py` exercises real local PDF rendering and output/encoding collisions; existing recognition tests still replace Tesseract. Golden held-out Russian financial reports, numeric exact-match/units validation, skew/merged cells and confidence/provenance still require an approved labelled corpus. No real OCR quality or automatic financial acceptance is established by these tests.

The synthetic real-engine smoke renders a generated PDF table with known numeric cells, uses the installed Tesseract `rus` engine and checks exact values. It is skipped if its engine/language/font prerequisite is absent, and is not a real financial-report holdout. Grid filtering rejects short text strokes before intersecting long line components; the detector assumes a prominent full-page ruled table (lines spanning at least one quarter of the image in their direction). Small tables, unruled/merged cells and skew require separate corpus qualification. The locally observed Tesseract version and dependency profile are recorded with validation results; package versions alone do not pin engine data.

## Maintained execution and native CI profile

`requirements-execution.in` resolves the compatible PyMuPDF 1.x API and current Pillow with
unit/lint/build tools. Regenerate its separate hash-locked `requirements-execution.txt` using
`uv pip compile requirements-execution.in --python-version 3.13 --generate-hashes --output-file requirements-execution.txt`.
The older `requirements-tested.txt` remains historical partial environment evidence, not the
current install recommendation. The profile was resolved on macOS arm64; the Linux CI run
separately qualifies its target instead of claiming a universal platform lock.

CI installs Tesseract/rus and a known DejaVu font, then sets `REQUIRE_TESSERACT_SMOKE=1`.
Missing native prerequisites fail this job rather than silently skipping the real-engine test.
Ordinary local pytest runs may still skip that one test when the engine/font is absent.
The generated numeric table smoke is not a held-out financial corpus or clinical/business
acceptance. Native engine/font/data versions remain part of a target-runtime qualification.

### Recognized text preservation

Cell extraction trims surrounding whitespace but preserves currency symbols, operators,
quotes and formula-like text. The previous blanket character filter could silently turn
`$100` into `100` or `2/3` into `23`; it has been removed. Spreadsheet escaping still occurs
at CSV serialization, separately from source recognition. cp1251 encoding continues to fail
explicitly before publishing a file when a recognized character cannot be represented.
Preserving symbols does not correct OCR errors or establish numeric/units accuracy.
