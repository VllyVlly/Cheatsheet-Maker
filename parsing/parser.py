from docling.document_converter import DocumentConverter
from io import BytesIO
from docling.datamodel.base_models import DocumentStream

def parse(converter: DocumentConverter, file_bytes, file_name):
    if converter is None: 
        print("Converter not found")
        return
    if file_bytes is None or file_name is None: 
        print("File not found")
        return
    buf = BytesIO(file_bytes)
    source = DocumentStream(name = file_name, stream = buf)
    return converter.convert(source).document.export_to_markdown()


def organize_parsed(ai_response):
    result = {}
    for entry in ai_response:
        if entry.section in result:
            result[entry.section].append(entry)
        else:
            result[entry.section] = [entry]
    return result

