# Howes — PDF → DOCX extractor

Mini app to extract the first 3 and last 3 words of each chapter from a PDF and produce a DOCX report.

Quick start (macOS / Linux):

1. Create a venv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the app:

```bash
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5001
```

3. Open http://localhost:5001 and upload a PDF.

Notes:
- The app attempts to auto-detect chapter starts using simple heuristics (lines starting with "Chapitre" or all-uppercase headings). If detection fails you can provide page ranges manually.
- The app uses PyMuPDF to extract text and `python-docx` to generate the result.
