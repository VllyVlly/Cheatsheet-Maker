import io
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from backend.app import app
from latex.assembler import assemble_latex
from latex.settings import FormatSettings
from parsing.errors import DocumentParsingError


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.previous_directory = app.config['OUTPUT_DIRECTORY']
        app.config['OUTPUT_DIRECTORY'] = Path(self.directory.name)

    def tearDown(self):
        app.config['OUTPUT_DIRECTORY'] = self.previous_directory
        self.directory.cleanup()

    def upload(self, **fields):
        return self.client.post('/api/generate', data={
            'files': (io.BytesIO(b'%PDF-test'), 'lecture.pdf'),
            **fields,
        })

    def test_missing_file(self):
        self.assertEqual(self.client.post('/api/generate').status_code, 400)

    def test_cors_only_allows_local_frontend_origins(self):
        allowed = self.client.post('/api/generate', headers={'Origin': 'http://127.0.0.1:5173'})
        self.assertEqual(allowed.headers.get('Access-Control-Allow-Origin'), 'http://127.0.0.1:5173')
        rejected = self.client.post('/api/generate', headers={'Origin': 'https://unrelated.example'})
        self.assertNotIn('Access-Control-Allow-Origin', rejected.headers)

    def test_invalid_second_file_is_not_silently_discarded(self):
        response = self.upload(files=[
            (io.BytesIO(b'first'), 'first.pdf'),
            (io.BytesIO(b'second'), 'second.txt'),
        ])
        self.assertEqual(response.status_code, 400)
        self.assertIn('second.txt', response.json['error'])

    def test_invalid_settings_and_unsupported_files(self):
        for settings in ['{', '{"columns": 5}', '{"font_size": "invalid"}', '{"margin": "0in"}', '{"margin": "1in}bad"}']:
            with self.subTest(settings=settings):
                self.assertEqual(self.upload(settings=settings).status_code, 400)
        self.assertEqual(self.upload(files=(io.BytesIO(b'text'), 'lecture.txt')).status_code, 400)
        self.assertEqual(self.upload(files=(io.BytesIO(b''), 'empty.pdf')).status_code, 400)

    def test_missing_api_key(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': ''}):
            self.assertEqual(self.upload().status_code, 503)

    def test_generation_and_downloads(self):
        def generate(client, contents, **options):
            output = Path(options['output_dir']) / options['output_name']
            output.with_suffix('.pdf').write_bytes(b'%PDF-test')
            output.with_suffix('.tex').write_text('LaTeX source', encoding='utf-8')
            return str(output.with_suffix('.pdf'))

        pipeline = types.ModuleType('backend.pipeline')
        pipeline.generate_cheatsheet = MagicMock(side_effect=generate)
        google = types.ModuleType('google')
        google.genai = MagicMock()

        with patch.dict(sys.modules, {'backend.pipeline': pipeline, 'google': google}), patch.dict(os.environ, {'GEMINI_API_KEY': 'test'}):
            response = self.upload(
                files=[
                    (io.BytesIO(b'pdf content'), 'lecture.PDF'),
                    (io.BytesIO(b'word content'), 'notes.docx'),
                    (io.BytesIO(b'slide content'), 'slides.pptx'),
                ],
                settings='{"columns": 3, "orientation": "landscape"}',
                classifier_prompt='Keep definitions',
                summarizer_prompt='Short examples',
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(pipeline.generate_cheatsheet.call_args.args[1], [
                ('lecture.PDF', b'pdf content'),
                ('notes.docx', b'word content'),
                ('slides.pptx', b'slide content'),
            ])
            options = pipeline.generate_cheatsheet.call_args.kwargs
            self.assertEqual(options['settings'].columns, 3)
            self.assertEqual(options['extra_classifier'], 'Keep definitions')
            self.assertEqual(options['extra_summarizer'], 'Short examples')
            pdf = self.client.get(response.json['pdf_url'])
            self.assertEqual(pdf.status_code, 200)
            self.assertEqual(pdf.mimetype, 'application/pdf')
            self.assertIn('inline', pdf.headers['Content-Disposition'])
            pdf.close()
            with self.client.get(response.json['tex_url']) as tex:
                self.assertEqual(tex.data, b'LaTeX source')
            second = self.upload()
            self.assertNotEqual(response.json['pdf_url'], second.json['pdf_url'])

            legacy = self.client.post('/generate', data={'file': (io.BytesIO(b'legacy'), 'old.pdf')})
            self.assertEqual(legacy.status_code, 200)
            self.assertEqual(pipeline.generate_cheatsheet.call_args.args[1], [('old.pdf', b'legacy')])

    def test_upload_limits(self):
        with patch.dict(app.config, {'MAX_FILES': 1}):
            response = self.upload(files=[
                (io.BytesIO(b'first'), 'first.pdf'),
                (io.BytesIO(b'second'), 'second.pdf'),
            ])
            self.assertEqual(response.status_code, 400)

        with patch.dict(app.config, {'MAX_FILE_SIZE': 4}):
            response = self.upload(files=(io.BytesIO(b'12345'), 'large.pdf'))
            self.assertEqual(response.status_code, 400)
            self.assertIn('large.pdf', response.json['error'])

        with patch.dict(app.config, {'MAX_TOTAL_FILE_SIZE': 8}):
            response = self.upload(files=[
                (io.BytesIO(b'12345'), 'first.pdf'),
                (io.BytesIO(b'12345'), 'second.pdf'),
            ])
            self.assertEqual(response.status_code, 400)
            self.assertIn('combined', response.json['error'])

        with patch.dict(app.config, {'MAX_CONTENT_LENGTH': 16}):
            self.assertEqual(self.upload().status_code, 413)

    def test_parse_failure_identifies_the_file(self):
        pipeline = types.ModuleType('backend.pipeline')
        pipeline.generate_cheatsheet = MagicMock(side_effect=DocumentParsingError('Could not parse lecture.pdf.'))
        google = types.ModuleType('google')
        google.genai = MagicMock()
        with patch.dict(sys.modules, {'backend.pipeline': pipeline, 'google': google}), patch.dict(os.environ, {'GEMINI_API_KEY': 'test'}):
            with self.assertLogs(app.logger, level='WARNING'):
                response = self.upload()
            self.assertEqual(response.status_code, 400)
            self.assertIn('lecture.pdf', response.json['error'])

    def test_generation_failure_returns_json(self):
        pipeline = types.ModuleType('backend.pipeline')
        pipeline.generate_cheatsheet = MagicMock(side_effect=RuntimeError('test failure'))
        google = types.ModuleType('google')
        google.genai = MagicMock()
        with patch.dict(sys.modules, {'backend.pipeline': pipeline, 'google': google}), patch.dict(os.environ, {'GEMINI_API_KEY': 'test'}):
            with self.assertLogs(app.logger, level='ERROR'):
                response = self.upload()
            self.assertEqual(response.status_code, 500)
            self.assertIn('error', response.json)

    def test_download_path_validation(self):
        self.assertEqual(self.client.get('/api/downloads/not-a-generated-file.pdf').status_code, 404)
        self.assertEqual(self.client.get('/api/downloads/' + 'a' * 32 + '.py').status_code, 404)

    def test_landscape_and_section_escaping(self):
        source = assemble_latex({'Terms & definitions': []}, FormatSettings(orientation='landscape'))
        self.assertIn('margin=1in,landscape', source)
        self.assertIn(r'Terms \& definitions', source)


if __name__ == '__main__':
    unittest.main()
