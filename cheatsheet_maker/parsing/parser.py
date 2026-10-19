from io import BytesIO
from pathlib import Path

from ..errors import DocumentParsingError


def build_converter(formula_enrichment=True, ocr=True, device="auto"):
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
    from docling.datamodel.pipeline_options import PdfPipelineOptions

    opts = PdfPipelineOptions()
    opts.do_formula_enrichment = formula_enrichment
    opts.do_ocr = ocr
    opts.accelerator_options = AcceleratorOptions(device=AcceleratorDevice(device))
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )


def parse_docling(converter, file_bytes, file_name):
    from docling.datamodel.base_models import DocumentStream

    source = DocumentStream(name=file_name, stream=BytesIO(file_bytes))
    return converter.convert(source).document.export_to_markdown()


def parse_files(files, converters=None, device="auto", ocr=True, formula_enrichment=True):
    if not files:
        raise DocumentParsingError("Choose at least one lecture file.")

    results = []
    if converters is None:
        converters = {}

    for file_name, file_bytes in files:
        file_name = Path(file_name.replace("\\", "/")).name
        extension = Path(file_name).suffix.lower()
        if extension not in {".pdf", ".docx", ".pptx"}:
            raise DocumentParsingError(f"{file_name}: unsupported file type. Choose PDF, DOCX, or PPTX.")
        if not file_bytes:
            raise DocumentParsingError(f"{file_name}: the file is empty.")

        try:
            if extension == ".pdf":
                parsed = parse_pdf(file_bytes, converters, device=device, ocr=ocr, formula_enrichment=formula_enrichment)
            else:
                if "document" not in converters:
                    converters["document"] = build_converter(formula_enrichment=formula_enrichment, ocr=ocr, device=device)
                parsed = parse_docling(converters["document"], file_bytes, file_name)
        except Exception as error:
            raise DocumentParsingError(f"Could not parse {file_name}. Check that the file is valid and is not password-protected.") from error

        if not parsed or not parsed.strip():
            raise DocumentParsingError(f"{file_name}: no readable content was found.")
        results.append(f"# Source file: {file_name}\n\n{parsed}")

    return "\n\n---\n\n".join(results)


def parse_pdf(file_bytes, converters=None, device="auto", ocr=True, formula_enrichment=True):
    import pymupdf

    if converters is None:
        converters = {}
    results = []

    with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text = page.get_text()
            has_math = looks_like_math(page)
            if text.strip() and not has_math:
                results.append(text)
                continue

            converter_name = "math" if has_math else "ocr"
            if converter_name not in converters:
                converters[converter_name] = build_converter(formula_enrichment=formula_enrichment, ocr=ocr and not has_math, device=device)

            with pymupdf.open() as one_page:
                one_page.insert_pdf(doc, from_page=page.number, to_page=page.number)
                page_bytes = one_page.tobytes()
                parsed = parse_docling(converters[converter_name], page_bytes, f"page_{page.number}.pdf")
                results.append(parsed)

    return "\n\n".join(results)


def looks_like_math(page):
    text = page.get_text()
    math_count = 0
    for ch in text:
        code = ord(ch)
        if 0x2200 <= code <= 0x22FF or 0x0370 <= code <= 0x03FF:
            math_count += 1
    return math_count >= 3


def organize_parsed(ai_response):
    result = {}
    for entry in ai_response:
        if entry.section in result:
            result[entry.section].append(entry)
        else:
            result[entry.section] = [entry]
    return result
