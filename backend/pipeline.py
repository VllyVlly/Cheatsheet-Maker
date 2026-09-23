import os
from pathlib import Path

from google import genai
from liteparse import LiteParse

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)

from latex.assembler import assemble_latex, compile_latex
from latex.settings import FormatSettings
from parsing.classifier import classify
from parsing.parser import organize_parsed, parse, parse_liteparse
from parsing.summarizer import summarizer


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
                        settings=FormatSettings(), output_name="cheatsheet", extra_classifier="", extra_summarizer=""):
    parsed = parse_fn(parser, file_bytes, filename)   
    classified = classify(client, parsed, extra_prompt=extra_classifier)
    summarized = summarizer(client, classified, extra_prompt=extra_summarizer)
    organized = organize_parsed(summarized)
    latex = assemble_latex(organized, settings)
    pdf_path = compile_latex(latex, filename=output_name)
    if pdf_path is None:
        raise RuntimeError("LaTeX compilation failed")
    return pdf_path

