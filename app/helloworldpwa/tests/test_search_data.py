from pathlib import Path

from helloworldpwa.Search_data import search_documents


def test_search_documents_matches_keyword_and_extension(tmp_path: Path):
    docs_dir = tmp_path / "Documents"
    docs_dir.mkdir()

    book = docs_dir / "math_workbook.pdf"
    book.write_bytes(b"example")

    other = docs_dir / "notes.txt"
    other.write_bytes(b"example")

    results = search_documents(keyword="workbook", search_root=str(tmp_path), extensions=[".pdf"])

    assert len(results) == 1
    assert results[0]["name"] == "math_workbook.pdf"
    assert results[0]["path"] == str(book)
