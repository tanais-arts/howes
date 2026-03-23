import os
import json
import tempfile
from flask import Flask, request, send_file, render_template, redirect, url_for
from pdf_parser import extract_pages_text, detect_chapter_starts, build_chapter_ranges, extract_first_last_words
from docx_generator import create_report

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    f = request.files.get('pdf')
    if not f:
        return 'Missing pdf', 400
    autodetect = bool(request.form.get('autodetect'))
    ranges_field = request.form.get('ranges','').strip()

    tmpfd, tmppath = tempfile.mkstemp(suffix='.pdf')
    os.close(tmpfd)
    f.save(tmppath)

    pages = extract_pages_text(tmppath)
    page_count = len(pages)

    ranges = None
    if ranges_field:
        try:
            ranges = json.loads(ranges_field)
        except Exception:
            ranges = None

    chapters = []
    if autodetect and not ranges:
        starts = detect_chapter_starts(pages)
        if starts:
            ranges = build_chapter_ranges(starts, page_count)

    if not ranges:
        # No ranges: return a simple page asking for manual ranges
        os.unlink(tmppath)
        return ("<p>Impossible d'identifier clairement les chapitres.</p>"
                "<p>Renseignez manuellement les plages de pages (JSON array) et renvoyez le formulaire.</p>"
                "<p><a href='/'>Retour</a></p>"), 200

    # ranges is a list of [start,end]
    for r in ranges:
        try:
            start = int(r[0]); end = int(r[1])
        except Exception:
            continue
        first, last = extract_first_last_words(pages, start, end, n=3)
        title = f'Chapitre {start+1}'
        chapters.append({'title': title, 'start': start, 'end': end, 'first': first, 'last': last})

    docx_path = create_report(chapters)
    os.unlink(tmppath)
    return send_file(docx_path, as_attachment=True, download_name='howes_report.docx')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
