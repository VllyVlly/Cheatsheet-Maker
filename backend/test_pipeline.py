from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from backend.pipeline import generate_cheatsheet


class PipelineTests(unittest.TestCase):
    def test_web_adapter_passes_documents_and_settings_to_public_package(self):
        files = [('lecture.pdf', b'pdf'), ('notes.docx', b'word')]
        client = object()
        result = SimpleNamespace(pdf_path='output/result.pdf')
        maker = MagicMock()
        maker.__enter__.return_value = maker
        maker.generate.return_value = result

        with patch('backend.pipeline.CheatsheetMaker', return_value=maker) as factory:
            path = generate_cheatsheet(client, files, extra_classifier='Definitions', extra_summarizer='Short examples')

        factory.assert_called_once_with(client=client)
        self.assertEqual(path, 'output/result.pdf')
        self.assertEqual(maker.generate.call_args.args[0], files)
        self.assertEqual(maker.generate.call_args.kwargs['extra_classifier'], 'Definitions')
        self.assertEqual(maker.generate.call_args.kwargs['extra_summarizer'], 'Short examples')

    def test_web_adapter_keeps_legacy_pdf_bytes(self):
        maker = MagicMock()
        maker.__enter__.return_value = maker
        maker.generate.return_value = SimpleNamespace(pdf_path='output/result.pdf')

        with patch('backend.pipeline.CheatsheetMaker', return_value=maker):
            generate_cheatsheet(object(), b'legacy pdf bytes')

        self.assertEqual(maker.generate.call_args.args[0], [('lecture.pdf', b'legacy pdf bytes')])


if __name__ == '__main__':
    unittest.main()
