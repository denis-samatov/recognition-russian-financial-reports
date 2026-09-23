from pathlib import Path

import cv2 as cv
import numpy as np
import pytest

import main
import recognition


def test_unreadable_image_has_clear_error(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Could not read image"):
        recognition.parse_img_to_csv_data(tmp_path / "missing.png")


def test_image_without_grid_has_clear_error(tmp_path: Path) -> None:
    path = tmp_path / "blank.png"
    assert cv.imwrite(str(path), np.full((100, 100, 3), 255, dtype=np.uint8))

    with pytest.raises(ValueError, match="No table grid detected"):
        recognition.parse_img_to_csv_data(path)


def test_grid_produces_only_cell_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "grid.png"
    image = np.full((400, 400, 3), 255, dtype=np.uint8)
    for coordinate in (40, 200, 360):
        cv.line(image, (coordinate, 40), (coordinate, 360), (0, 0, 0), 2)
        cv.line(image, (40, coordinate), (360, coordinate), (0, 0, 0), 2)
    assert cv.imwrite(str(path), image)
    monkeypatch.setattr(recognition.pytesseract, "image_to_string", lambda *_args, **_kwargs: "cell")

    data = recognition.parse_img_to_csv_data(path)

    assert data == [["cell", "cell"], ["cell", "cell"]]


def test_cli_rejects_unsupported_extension(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["pdf2csv", str(tmp_path / "notes.txt")])

    with pytest.raises(SystemExit, match="2"):
        main.main()
