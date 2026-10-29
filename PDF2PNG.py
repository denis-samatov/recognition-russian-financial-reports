import logging
from pathlib import Path
from typing import Optional

import fitz

from output_files import publish_bytes

logger = logging.getLogger(__name__)

OUTPUT_DIR_NAME = "table in PNG"


def convert_pdf2png(input_file: Path, output_dir: Optional[Path] = None) -> list[Path]:
    """Converts each page of a PDF file to a PNG image.

    This function takes a path to a PDF file, iterates through each page,
    and saves each page as a separate PNG file. The output PNG files are
    saved in a directory named "table in PNG".

    Args:
        input_file: The path to the input PDF file.

    Returns:
        A list of paths for the generated PNG images.
    """
    output_files: list[Path] = []
    output_dir = Path.cwd() / OUTPUT_DIR_NAME if output_dir is None else Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Open the document
    with fitz.open(input_file) as doc:
        # Walk the pages
        for pg in range(doc.page_count):
            # Select the page
            page = doc[pg]
            # The PDF page is rendered to a full 1056x816 image, then a
            # screenshot is taken of that image.
            # zoom = 1.33333333 -----> image size = 1056 x 816
            # zoom = 2 ---> 2x default resolution (crisp text, poor image legibility) = smaller file/image size = 1584 x 1224
            # zoom = 4 ---> 4x default resolution (crisp text, poor image legibility) = larger file size
            # zoom = 8 ---> 8x default resolution (crisp text, legible image) = large file size
            zoom_x = 2
            zoom_y = 2
            # Pre-rotate applies rotation if needed.
            rotate = int(0)
            mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            output_file = output_dir / f"{input_file.stem}_page_{pg + 1}.png"
            publish_bytes(output_file, pix.tobytes("png"))
            output_files.append(output_file)

        report = {
            "Source file": input_file.name,
            "Page count": str(doc.page_count),
            "Output file(s)": str(output_files),
        }
    # Brief summary log
    logger.info("########################### File created ###########################")
    logger.info("\n".join(f"{key}: {value}" for key, value in report.items()))
    logger.info("##################################################################")

    return output_files
