import json
import os
from pathlib import Path
from uuid import uuid4

from flask import Flask, request, send_from_directory, url_for
from flask_cors import CORS
from pydantic import ValidationError

from latex.settings import FormatSettings
from parsing.errors import DocumentParsingError

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 101 * 1024 * 1024
app.config['MAX_FILES'] = 10
app.config['MAX_FILE_SIZE'] = 25 * 1024 * 1024
app.config['MAX_TOTAL_FILE_SIZE'] = 100 * 1024 * 1024
app.config['OUTPUT_DIRECTORY'] = Path(__file__).resolve().parent.parent / 'output'
CORS(app, origins=['http://127.0.0.1:5173', 'http://localhost:5173'])


@app.post('/generate')
@app.post('/api/generate')
def generate():
    files = request.files.getlist('files') + request.files.getlist('file')
    if not files or any(not file.filename for file in files):
        return {'error': 'Choose one or more lecture files before generating.'}, 400
    if len(files) > app.config['MAX_FILES']:
        return {'error': 'Choose no more than 10 files per cheatsheet.'}, 400

    for file in files:
        if Path(file.filename).suffix.lower() not in {'.pdf', '.docx', '.pptx'}:
            return {'error': f'{file.filename}: choose a PDF, DOCX, or PPTX file.'}, 400

    try:
        settings = FormatSettings.model_validate(json.loads(request.form.get('settings', '{}')))
    except (ValueError, ValidationError):
        return {'error': 'Check your format settings. Use 1–4 columns, a supported font size, and a positive margin such as 1in.'}, 400

    classifier_prompt = request.form.get('classifier_prompt', '')
    summarizer_prompt = request.form.get('summarizer_prompt', '')
    if max(len(classifier_prompt), len(summarizer_prompt)) > 10000:
        return {'error': 'Keep each custom prompt under 10,000 characters.'}, 400

    documents = []
    total_size = 0
    for file in files:
        contents = file.read(app.config['MAX_FILE_SIZE'] + 1)
        if not contents or len(contents) > app.config['MAX_FILE_SIZE']:
            return {'error': f'{file.filename}: choose a nonempty file no larger than 25 MB.'}, 400
        total_size += len(contents)
        if total_size > app.config['MAX_TOTAL_FILE_SIZE']:
            return {'error': 'Keep the combined file size at or below 100 MB.'}, 400
        documents.append((file.filename, contents))

    if not os.getenv('GEMINI_API_KEY'):
        return {'error': 'The server needs GEMINI_API_KEY configured before it can generate cheatsheets.'}, 503

    try:
        from google import genai
        from backend.pipeline import generate_cheatsheet

        output_name = uuid4().hex
        output_directory = Path(app.config['OUTPUT_DIRECTORY'])
        output_directory.mkdir(parents=True, exist_ok=True)

        with genai.Client(api_key=os.environ['GEMINI_API_KEY']) as client:
            generate_cheatsheet(
                client,
                documents,
                settings=settings,
                output_name=output_name,
                output_dir=str(output_directory),
                extra_classifier=classifier_prompt,
                extra_summarizer=summarizer_prompt,
            )

        return {
            'pdf_url': url_for('download', filename=f'{output_name}.pdf'),
            'tex_url': url_for('download', filename=f'{output_name}.tex'),
        }
    except DocumentParsingError as error:
        app.logger.warning('Document parsing failed', exc_info=True)
        return {'error': str(error)}, 400
    except Exception:
        app.logger.exception('Cheatsheet generation failed')
        return {'error': 'Generation failed. Please try again or check the Flask logs for details.'}, 500


@app.get('/api/downloads/<filename>')
def download(filename):
    name = Path(filename)
    if name.suffix not in {'.pdf', '.tex'} or len(name.stem) != 32 or any(character not in '0123456789abcdef' for character in name.stem):
        return {'error': 'File not found.'}, 404

    return send_from_directory(
        app.config['OUTPUT_DIRECTORY'],
        filename,
        mimetype='application/pdf' if name.suffix == '.pdf' else 'application/x-tex',
        as_attachment=name.suffix == '.tex',
        download_name=f'cheatsheet{name.suffix}',
    )


@app.errorhandler(413)
def upload_too_large(error):
    return {'error': 'This upload is too large. Use up to 10 files, 25 MB per file, and 100 MB total.'}, 413


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=False)
