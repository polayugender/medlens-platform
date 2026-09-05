import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, Any, List, Tuple
from app.config import settings

def parse_pdf_document(file_path: Path) -> Dict[str, Any]:
    """
    Parses a PDF document using PyMuPDF:
    - Extracts full text with line and page numbers
    - Renders preview images of each page for side-by-side inspection
    - Collects document metadata
    """
    doc = fitz.open(file_path)
    page_count = len(doc)
    full_text_pages: List[str] = []
    lines_with_page: List[Dict[str, Any]] = []
    rendered_previews: List[str] = []

    report_stem = file_path.stem

    for page_idx in range(page_count):
        page = doc[page_idx]
        page_text = page.get_text("text")
        full_text_pages.append(page_text)

        # Extract lines for snippet indexing
        lines = page_text.splitlines()
        for l_idx, line in enumerate(lines):
            clean_line = line.strip()
            if clean_line:
                lines_with_page.append({
                    "page": page_idx + 1,
                    "line_number": l_idx + 1,
                    "text": clean_line
                })

        # Render first page preview image for instant viewing
        if page_idx < 3: # render up to 3 pages
            pix = page.get_pixmap(dpi=150)
            preview_filename = f"{report_stem}_p{page_idx + 1}.png"
            preview_path = settings.PREVIEWS_DIR / preview_filename
            pix.save(str(preview_path))
            rendered_previews.append(f"/storage/previews/{preview_filename}")

    combined_text = "\n\n--- PAGE BREAK ---\n\n".join(full_text_pages)
    doc.close()

    return {
        "page_count": page_count,
        "raw_text": combined_text,
        "lines": lines_with_page,
        "previews": rendered_previews
    }

def find_snippet_in_text(text: str, test_name: str, value: str) -> Tuple[str, int]:
    """
    Locates the most precise matching line in the report text to serve as the raw_snippet.
    Returns (raw_snippet, page_number).
    """
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        # Case-insensitive check for test name in line
        if test_name.lower() in line.lower() and (value.lower() in line.lower() or any(char.isdigit() for char in line)):
            return line.strip(), 1
    
    # Fallback to test name line
    for line in lines:
        if test_name.lower() in line.lower():
            return line.strip(), 1

    return f"{test_name}: {value}", 1
