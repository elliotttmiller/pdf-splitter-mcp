from pathlib import Path
import shutil

from app.services.pdf_engine import PDFEngine


def test_split_matches_page_count():
    src_dir = Path("data") / "temp"
    # find an input_*.pdf produced by previous run
    inputs = list(src_dir.glob("input_*.pdf"))
    assert inputs, "No input_*.pdf found in data/temp to run verification against"

    input_pdf = inputs[0]

    # create an isolated temp directory for outputs
    out_dir = Path("data") / "temp_test"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    engine = PDFEngine(out_dir)
    page_files, page_count = engine.split(input_pdf)

    # page_files should be a list of filenames and its length should equal page_count
    assert isinstance(page_files, list)
    assert len(page_files) == page_count

    # ensure files were created
    for fname in page_files:
        p = out_dir / fname
        assert p.exists() and p.stat().st_size > 0

    # cleanup
    shutil.rmtree(out_dir)
