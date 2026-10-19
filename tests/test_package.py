import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from cheatsheet_maker import CheatsheetMaker, DocumentParsingError, FormatSettings
from cheatsheet_maker.inputs import load_documents
from cheatsheet_maker.latex.assembler import compile_latex
from cheatsheet_maker.parsing.jsonformat import ExtractedItem, ItemType


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.addCleanup(self.directory.cleanup)
        self.output = Path(self.directory.name)
        self.item = ExtractedItem(type=ItemType.definition, content='A useful definition.', section='Basics')

    def test_parse_needs_no_key_and_reuses_converters(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': ''}):
            maker = CheatsheetMaker(device='cpu', ocr=False)
            with patch('cheatsheet_maker.maker.parse_files', return_value='Notes') as parse:
                self.assertEqual(maker.parse({'first.pdf': b'first'}), 'Notes')
                maker.parse({'second.docx': b'second'})

        first_options = parse.call_args_list[0].kwargs
        second_options = parse.call_args_list[1].kwargs
        self.assertIs(first_options['converters'], second_options['converters'])
        self.assertEqual(first_options['device'], 'cpu')
        self.assertFalse(first_options['ocr'])

    def test_paths_and_colab_mapping_produce_identical_inputs(self):
        first = self.output / 'lecture.pdf'
        first.write_bytes(b'pdf')
        self.assertEqual(load_documents(first), [('lecture.pdf', b'pdf')])
        self.assertEqual(load_documents([str(first)]), load_documents({'lecture.pdf': b'pdf'}))

    def test_input_validation(self):
        invalid = [[], {'empty.pdf': b''}, {'file.txt': b'text'}, [(None, b'pdf')], ['unsupported.txt']]
        for files in invalid:
            with self.subTest(files=files):
                with self.assertRaises((DocumentParsingError, TypeError)):
                    load_documents(files)
        with self.assertRaises(DocumentParsingError):
            load_documents([(f'{index}.pdf', b'pdf') for index in range(11)])

    def test_mixed_documents_generate_one_result_without_compiler(self):
        maker = CheatsheetMaker(client=object(), model='my-model')
        with (
            patch('cheatsheet_maker.parsing.parser.parse_pdf', return_value='PDF material'),
            patch('cheatsheet_maker.parsing.parser.build_converter'),
            patch('cheatsheet_maker.parsing.parser.parse_docling', side_effect=['Word material', 'Slide material']),
            patch('cheatsheet_maker.maker.classify_gemini', return_value=[self.item]) as classify,
            patch('cheatsheet_maker.maker.summarizer_gemini', return_value=[self.item]) as summarize,
            patch('cheatsheet_maker.maker.compile_latex') as compile_pdf,
        ):
            result = maker.generate(
                {'lecture.pdf': b'pdf', 'notes.docx': b'word', 'slides.pptx': b'slides'},
                settings=FormatSettings(columns=3),
                output_dir=self.output,
                extra_classifier='Definitions',
                extra_summarizer='Short examples',
                compile_pdf=False,
            )

        for content in ['PDF material', 'Word material', 'Slide material']:
            self.assertIn(content, result.markdown)
        self.assertIn(r'\begin{multicols}{3}', result.tex_path.read_text(encoding='utf-8'))
        self.assertIsNone(result.pdf_path)
        self.assertEqual(result.items, [self.item])
        self.assertEqual(classify.call_args.kwargs, {'model': 'my-model', 'extra_prompt': 'Definitions'})
        self.assertEqual(summarize.call_args.kwargs, {'model': 'my-model', 'extra_prompt': 'Short examples'})
        compile_pdf.assert_not_called()

    def test_saved_markdown_skips_parsing_and_default_outputs_are_unique(self):
        maker = CheatsheetMaker(client=object())
        with (
            patch('cheatsheet_maker.maker.parse_files') as parse,
            patch('cheatsheet_maker.maker.classify_gemini', return_value=[self.item]),
            patch('cheatsheet_maker.maker.summarizer_gemini', return_value=[self.item]),
        ):
            first = maker.generate_from_markdown('Saved notes', output_dir=self.output, compile_pdf=False)
            second = maker.generate_from_markdown('Saved notes', output_dir=self.output, compile_pdf=False)

        parse.assert_not_called()
        self.assertNotEqual(first.tex_path, second.tex_path)
        self.assertTrue(first.tex_path.is_file())
        self.assertTrue(second.tex_path.is_file())

    def test_invalid_output_name_is_rejected_before_model_calls(self):
        maker = CheatsheetMaker(client=object())
        with patch('cheatsheet_maker.maker.classify_gemini') as classify:
            for name in ['../escape', '/absolute', 'file.tex', 'a/b', 'a\\b']:
                with self.subTest(name=name), self.assertRaises(ValueError):
                    maker.generate_from_markdown('Notes', output_name=name, output_dir=self.output)
        classify.assert_not_called()

    def test_parse_failure_stops_before_classification(self):
        maker = CheatsheetMaker(client=object())
        with (
            patch('cheatsheet_maker.maker.parse_files', side_effect=DocumentParsingError('bad.pdf')),
            patch('cheatsheet_maker.maker.classify_gemini') as classify,
        ):
            with self.assertRaises(DocumentParsingError):
                maker.generate({'bad.pdf': b'broken'})
        classify.assert_not_called()

    def test_missing_key_does_not_start_parsing_or_create_outputs(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': ''}):
            maker = CheatsheetMaker()
            with patch('cheatsheet_maker.maker.parse_files') as parse:
                with self.assertRaisesRegex(ValueError, 'own Gemini API key'):
                    maker.generate({'file.pdf': b'pdf'}, output_dir=self.output)
        parse.assert_not_called()
        self.assertEqual(list(self.output.iterdir()), [])

    def test_client_is_lazy_and_only_owned_clients_are_closed(self):
        google = SimpleNamespace(genai=SimpleNamespace(Client=MagicMock()))
        with patch.dict(sys.modules, {'google': google}):
            with CheatsheetMaker(api_key='not-a-real-key') as maker:
                google.genai.Client.assert_not_called()
                self.assertNotIn('not-a-real-key', repr(maker))
                client = maker._get_client()
                self.assertIs(client, maker._get_client())
            client.close.assert_called_once()
            google.genai.Client.assert_called_once_with(api_key='not-a-real-key')

        external_client = MagicMock()
        with CheatsheetMaker(client=external_client):
            pass
        external_client.close.assert_not_called()

    def test_device_and_timeout_validation(self):
        for options in [{'device': 'invalid'}, {'compile_timeout': 0}, {'compile_timeout': float('inf')}]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                CheatsheetMaker(**options)

    def test_compiler_has_timeout_untrusted_mode_and_no_gemini_key(self):
        pdf = self.output / 'sheet.pdf'
        pdf.write_bytes(b'%PDF-test')
        with (
            patch('cheatsheet_maker.latex.assembler.shutil.which', return_value='tectonic'),
            patch('cheatsheet_maker.latex.assembler.subprocess.run', return_value=SimpleNamespace(returncode=0)) as run,
            patch.dict(os.environ, {'GEMINI_API_KEY': 'not-a-real-key', 'GOOGLE_APPLICATION_CREDENTIALS': 'private.json'}),
        ):
            self.assertEqual(compile_latex('source', self.output, 'sheet', timeout=30), str(pdf))

        self.assertIn('--untrusted', run.call_args.args[0])
        self.assertEqual(run.call_args.kwargs['timeout'], 30)
        self.assertEqual(run.call_args.kwargs['cwd'], self.output)
        environment = run.call_args.kwargs['env']
        self.assertEqual(environment['TECTONIC_UNTRUSTED_MODE'], '1')
        self.assertNotIn('GEMINI_API_KEY', environment)
        self.assertNotIn('GOOGLE_APPLICATION_CREDENTIALS', environment)

    def test_compiler_failure_and_missing_installation_are_explicit(self):
        with patch('cheatsheet_maker.latex.assembler.shutil.which', return_value=None):
            with self.assertRaisesRegex(FileNotFoundError, 'compile_pdf=False'):
                compile_latex('source', self.output)

        with patch('cheatsheet_maker.latex.assembler.shutil.which', return_value='tectonic'):
            with patch('cheatsheet_maker.latex.assembler.subprocess.run', side_effect=subprocess.TimeoutExpired('tectonic', 1)):
                with self.assertRaisesRegex(RuntimeError, 'exceeded'):
                    compile_latex('source', self.output, timeout=1)
            with patch('cheatsheet_maker.latex.assembler.subprocess.run', return_value=SimpleNamespace(returncode=1)):
                with self.assertRaisesRegex(RuntimeError, 'compilation failed'):
                    compile_latex('source', self.output)


if __name__ == '__main__':
    unittest.main()
