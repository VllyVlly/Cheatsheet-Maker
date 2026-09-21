from parsing.parser import parse, organize_parsed, parse_liteparse
from parsing.classifier import classify
from latex.assembler import assemble_latex, compile_latex
from parsing.summarizer import summarizer
from latex.settings import FormatSettings

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions, AcceleratorDevice, RapidOcrOptions
from docling.datamodel.base_models import InputFormat
from pathlib import Path
from google import genai

from liteparse import LiteParse

import os

def build_converter(formula_enrichment=True, ocr=True):
    opts = PdfPipelineOptions()
    opts.do_formula_enrichment = formula_enrichment
    opts.do_ocr = ocr
    opts.accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CUDA)
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )


def build_liteparse(ocr=True):
    return LiteParse(
        output_format="markdown",
        image_mode="off",
        ocr_enabled=ocr,
        quiet=True,
    )


def generate_cheatsheet(parse_fn, parser, client, file_bytes, filename,
                        settings=FormatSettings(), output_name="cheatsheet"):
    parsed = parse_fn(parser, file_bytes, filename)   
    classified = classify(client, parsed)
    summarized = summarizer(client, classified)
    organized = organize_parsed(summarized)
    latex = assemble_latex(organized, settings)
    pdf_path = compile_latex(latex, filename=output_name)
    if pdf_path is None:
        raise RuntimeError("LaTeX compilation failed")
    return pdf_path


if __name__ == "__main__":
    parser = build_liteparse()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    file_bytes = Path("lecture.pdf").read_bytes()
    print(generate_cheatsheet(parse_liteparse, parser, client,
                              file_bytes, "lecture.pdf"))