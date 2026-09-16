from parsing.parser import parse, organize_parsed
from parsing.classifier import classify
from latex.assembler import assemble_latex, compile_latex

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions, AcceleratorDevice
from docling.datamodel.base_models import InputFormat
from pathlib import Path
from google import genai

import os
import torch

print(torch.cuda.is_available())
pipeline_options = PdfPipelineOptions()
pipeline_options.do_formula_enrichment = True
pipeline_options.do_ocr = True
pipeline_options.accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CUDA)
converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})


file_bytes = Path("lecture.pdf").read_bytes()
result = parse(converter, file_bytes, "lecture.pdf")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
classified_result = classify(client, result)

organized_result = organize_parsed(classified_result)
latex_result = assemble_latex(organized_result)
final = compile_latex(latex_result)
