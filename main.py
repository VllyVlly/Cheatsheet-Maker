from parsing.parser import parse
from parsing.classifier import classify
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions, AcceleratorDevice
from docling.datamodel.base_models import InputFormat
from pathlib import Path
from google import genai
import os


pipeline_options = PdfPipelineOptions()
pipeline_options.do_formula_enrichment = True
pipeline_options.accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CPU)
converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})


file_bytes = Path("lecture.pdf").read_bytes()
result = parse(converter, file_bytes, "lecture.pdf")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
classified_result = classify(client, result)

for item in classified_result:
    print(item.type, "-", item.section, "-", item.content)
