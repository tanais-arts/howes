import fitz
import re

def extract_pages_text(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for p in doc:
        text = p.get_text("text") or ""
        pages.append(text)
    doc.close()
    return pages

def detect_chapter_starts(pages):
    starts = []
    title_rx = re.compile(r'^\s*(CHAPITRE|Chapitre|CHAP\b|CHAPTER|CHAP\.)', re.I)
    for i, text in enumerate(pages):
        # Inspect first lines
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not lines:
            continue
        # first non-empty line
        first = lines[0]
        if title_rx.search(first):
            starts.append(i)
            continue
        # uppercase line heuristic
        if len(first) > 3 and first.upper() == first and re.search(r'[A-ZÀ-ÖØ-Þ]', first):
            starts.append(i)
            continue
        # sometimes the page contains a sole word like "CHAPITRE" or roman numeral
        if re.match(r'^[IVXLC0-9]+$', first):
            starts.append(i)
            continue
    # dedupe and sort
    starts = sorted(set(starts))
    return starts

def build_chapter_ranges(starts, page_count):
    if not starts:
        return []
    ranges = []
    for idx, s in enumerate(starts):
        end = (starts[idx+1]-1) if idx+1 < len(starts) else (page_count-1)
        ranges.append((s, end))
    return ranges

def extract_first_last_words(pages, start, end, n=3):
    # join pages from start to end
    text = "\n".join(pages[start:end+1])
    # normalize apostrophes and spaces
    text = text.replace('\u2019', "'").replace('\u2018', "'")
    # tokenise on whitespace and strip punctuation
    words = re.findall(r"[\wÀ-ÖØ-öø-ÿ'-]+", text, re.UNICODE)
    if not words:
        return ([], [])
    first = words[:n]
    last = words[-n:]
    return (first, last)
