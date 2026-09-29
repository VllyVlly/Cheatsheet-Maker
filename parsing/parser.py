from docling.document_converter import DocumentConverter
from io import BytesIO
from docling.datamodel.base_models import DocumentStream
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)
import pymupdf

def build_converter(formula_enrichment=True, ocr=True):
    opts = PdfPipelineOptions()
    opts.do_formula_enrichment = formula_enrichment
    opts.do_ocr = ocr
    opts.accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CUDA)
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )


def parse_docling(converter: DocumentConverter, file_bytes, file_name):
    if converter is None: 
        print("Converter not found")
        return
    if file_bytes is None or file_name is None: 
        print("File not found")
        return
    buf = BytesIO(file_bytes)
    source = DocumentStream(name = file_name, stream = buf)
    return converter.convert(source).document.export_to_markdown()


def parse_pdf(file_bytes):
    results = {}                      
    converter_ocr = build_converter(formula_enrichment=True, ocr=True)
    converter_no_ocr = build_converter(formula_enrichment=True, ocr=False)

    with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            if looks_like_math(page):
                one_page = pymupdf.open() 
                one_page.insert_pdf(doc, from_page=page.number, to_page=page.number)
                page_bytes = one_page.tobytes()
                results[page.number] = parse_docling(converter_no_ocr, page_bytes, f"page_{page.number}.pdf")
            else:
                text = page.get_text()
                if text:
                    results[page.number] = text
                else:
                    one_page = pymupdf.open() 
                    one_page.insert_pdf(doc, from_page=page.number, to_page=page.number)
                    page_bytes = one_page.tobytes()
                    results[page.number] = parse_docling(converter_ocr, page_bytes, f"page_{page.number}.pdf")


    return "\n\n".join(results[n] for n in sorted(results))


def looks_like_math(page):
    text = page.get_text()
    math_count = 0
    for ch in text:
        code = ord(ch)
        if 0x2200 <= code <= 0x22FF or 0x0370 <= code <= 0x03FF:
            math_count += 1
    if math_count >= 3:
        return True
    return False


def organize_parsed(ai_response):
    result = {}
    for entry in ai_response:
        if entry.section in result:
            result[entry.section].append(entry)
        else:
            result[entry.section] = [entry]
    return result

