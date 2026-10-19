import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from parsing.errors import DocumentParsingError
from parsing.parser import parse_files


def make_document(text):
    page = SimpleNamespace(number=0, get_text=lambda: text)
    document = MagicMock()
    document.__enter__.return_value = document
    document.__iter__.return_value = [page]
    return document


class ParserTests(unittest.TestCase):
    def test_text_pdfs_keep_upload_order_without_loading_docling(self):
        pymupdf = MagicMock()
        pymupdf.open.side_effect = [make_document('First lecture'), make_document('Second lecture')]

        with patch.dict(sys.modules, {'pymupdf': pymupdf}), patch('cheatsheet_maker.parsing.parser.build_converter') as build:
            result = parse_files([('first.pdf', b'first'), ('second.PDF', b'second')])

        self.assertIn('# Source file: first.pdf\n\nFirst lecture', result)
        self.assertIn('# Source file: second.PDF\n\nSecond lecture', result)
        self.assertLess(result.index('First lecture'), result.index('Second lecture'))
        build.assert_not_called()
        self.assertEqual(pymupdf.open.call_count, 2)

    def test_word_and_powerpoint_share_a_converter(self):
        converter = object()
        with patch('cheatsheet_maker.parsing.parser.build_converter', return_value=converter) as build:
            with patch('cheatsheet_maker.parsing.parser.parse_docling', side_effect=['Word notes', 'Slide notes']) as parse:
                result = parse_files([('notes.docx', b'word'), ('slides.pptx', b'slides')])

        build.assert_called_once()
        self.assertEqual(parse.call_args_list[0].args, (converter, b'word', 'notes.docx'))
        self.assertEqual(parse.call_args_list[1].args, (converter, b'slides', 'slides.pptx'))
        self.assertIn('Word notes', result)
        self.assertIn('Slide notes', result)

    def test_scanned_pdfs_reuse_ocr_converter_and_close_page_documents(self):
        pymupdf = MagicMock()
        first_page = make_document('')
        second_page = make_document('')
        pymupdf.open.side_effect = [make_document(''), first_page, make_document(''), second_page]

        with patch.dict(sys.modules, {'pymupdf': pymupdf}), patch('cheatsheet_maker.parsing.parser.build_converter') as build:
            with patch('cheatsheet_maker.parsing.parser.parse_docling', side_effect=['Scanned first', 'Scanned second']):
                result = parse_files([('first.pdf', b'first'), ('second.pdf', b'second')])

        build.assert_called_once_with(formula_enrichment=True, ocr=True, device="auto")
        first_page.__exit__.assert_called_once()
        second_page.__exit__.assert_called_once()
        self.assertIn('Scanned first', result)
        self.assertIn('Scanned second', result)

    def test_math_pages_use_converter_without_ocr(self):
        pymupdf = MagicMock()
        pymupdf.open.side_effect = [make_document('α + β = γ'), make_document('')]
        with patch.dict(sys.modules, {'pymupdf': pymupdf}), patch('cheatsheet_maker.parsing.parser.build_converter') as build:
            with patch('cheatsheet_maker.parsing.parser.parse_docling', return_value='Recovered equation'):
                result = parse_files([('math.pdf', b'math')])

        build.assert_called_once_with(formula_enrichment=True, ocr=False, device="auto")
        self.assertIn('Recovered equation', result)

    def test_mixed_formats_keep_source_boundaries(self):
        with patch('cheatsheet_maker.parsing.parser.parse_pdf', return_value='PDF notes'):
            with patch('cheatsheet_maker.parsing.parser.build_converter'), patch('cheatsheet_maker.parsing.parser.parse_docling', side_effect=['Word notes', 'Slides']):
                result = parse_files([('lecture.pdf', b'pdf'), ('notes.docx', b'word'), ('slides.pptx', b'slides')])

        self.assertEqual(result.count('# Source file:'), 3)
        self.assertLess(result.index('PDF notes'), result.index('Word notes'))
        self.assertLess(result.index('Word notes'), result.index('Slides'))

    def test_failed_or_empty_document_does_not_return_partial_results(self):
        for second_result in [RuntimeError('invalid PDF'), '', '   ']:
            with self.subTest(result=second_result):
                with patch('cheatsheet_maker.parsing.parser.parse_pdf', side_effect=['Good notes', second_result]):
                    with self.assertRaisesRegex(DocumentParsingError, 'second.pdf'):
                        parse_files([('first.pdf', b'first'), ('second.pdf', b'second')])

    def test_missing_empty_and_unsupported_files(self):
        for files in [[], [('empty.pdf', b'')], [('file.txt', b'text')]]:
            with self.subTest(files=files):
                with self.assertRaises(DocumentParsingError):
                    parse_files(files)


if __name__ == '__main__':
    unittest.main()
