from pathlib import Path
import csv
import fitz
import pytest
from PDF2PNG import convert_pdf2png
from writeToCSV import write_csv

def test_csv_never_overwrites_existing_result(tmp_path):
    path = tmp_path / "report.csv"
    path.write_bytes(b"original")
    with pytest.raises(FileExistsError):
        write_csv(path, [["new"]])
    assert path.read_bytes() == b"original"

def test_unencodable_cell_does_not_leave_partial_file(tmp_path):
    path = tmp_path / "report.csv"
    with pytest.raises(UnicodeEncodeError):
        write_csv(path, [["ok"], ["emoji \U0001f600"]])
    assert not path.exists()
    assert not list(tmp_path.glob(".*.tmp"))

def test_csv_escapes_formulas_but_preserves_signed_numbers(tmp_path):
    path = tmp_path / "report.csv"
    write_csv(path, [["=1+1", "+cmd", "@SUM(A1)", "-1+2", "-3.5", "-1,25", "обычно"]])
    with path.open(encoding="cp1251", newline="") as file:
        assert next(csv.reader(file)) == ["'=1+1", "'+cmd", "'@SUM(A1)", "'-1+2", "-3.5", "-1,25", "обычно"]

def make_pdf(path):
    with fitz.open() as doc:
        doc.new_page(width=100, height=100)
        doc.save(path)

def test_pdf_no_clobber_and_explicit_output_directory(tmp_path, monkeypatch):
    source = tmp_path / "report.pdf"
    make_pdf(source)
    monkeypatch.chdir(tmp_path)
    first = convert_pdf2png(source)
    before = first[0].read_bytes()
    with pytest.raises(FileExistsError):
        convert_pdf2png(source)
    assert first[0].read_bytes() == before
    other = convert_pdf2png(source, output_dir=tmp_path / "separate")
    assert other[0].parent == tmp_path / "separate"

def test_cli_uses_explicit_output_directory_for_png(tmp_path, monkeypatch):
    import main
    source = tmp_path / "report.png"
    output = tmp_path / "results"
    monkeypatch.setattr("sys.argv", ["pdf2csv", str(source), "--output-dir", str(output)])
    monkeypatch.setattr(main, "parse_img_to_csv_data", lambda path: [["100"]])
    main.main()
    assert (output / "report.csv").is_file()
    assert not source.with_suffix(".csv").exists()


def test_real_tesseract_synthetic_numeric_grid(tmp_path):
    import shutil
    import os
    import pytesseract
    from PIL import Image, ImageDraw, ImageFont
    import recognition
    if shutil.which("tesseract") is None or "rus" not in pytesseract.get_languages(config=""):
        if os.environ.get("REQUIRE_TESSERACT_SMOKE") == "1":
            pytest.fail("CI requires real Tesseract with rus language")
        pytest.skip("Real Tesseract with rus language is required")
    candidates = [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
                  Path("/System/Library/Fonts/Supplemental/Arial.ttf")]
    font_path = next((path for path in candidates if path.is_file()), None)
    if font_path is None:
        if os.environ.get("REQUIRE_TESSERACT_SMOKE") == "1":
            pytest.fail("CI requires a Cyrillic-capable fixture font")
        pytest.skip("Synthetic fixture font unavailable")
    image = Image.new("RGB", (600, 600), "white")
    draw = ImageDraw.Draw(image)
    for coordinate in (30, 300, 570):
        draw.line((coordinate, 30, coordinate, 570), fill="black", width=3)
        draw.line((30, coordinate, 570, coordinate), fill="black", width=3)
    font = ImageFont.truetype(str(font_path), 55)
    for xy, value in [((70, 100), "100"), ((340, 100), "200"), ((70, 370), "300"), ((340, 370), "400")]:
        draw.text(xy, value, fill="black", font=font)
    png = tmp_path / "synthetic.png"
    image.save(png)
    pdf = tmp_path / "synthetic.pdf"
    with fitz.open() as document:
        page = document.new_page(width=600, height=600)
        page.insert_image(page.rect, filename=str(png))
        document.save(pdf)
    rendered = convert_pdf2png(pdf, output_dir=tmp_path / "rendered")
    data = recognition.parse_img_to_csv_data(rendered[0])
    assert [[text.strip() for text in row] for row in data] == [["100", "200"], ["300", "400"]]
    csv_path = tmp_path / "synthetic.csv"
    write_csv(csv_path, data)
    assert csv_path.is_file()
