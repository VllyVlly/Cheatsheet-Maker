from collections.abc import Mapping
from pathlib import Path

from .errors import DocumentParsingError

MAX_FILES = 10
MAX_FILE_SIZE = 25 * 1024 * 1024
MAX_TOTAL_FILE_SIZE = 100 * 1024 * 1024


def load_documents(files):
    if isinstance(files, (str, Path)):
        files = [files]
    elif isinstance(files, Mapping):
        files = files.items()

    documents = []
    total_size = 0

    for entry in files:
        if len(documents) >= MAX_FILES:
            raise DocumentParsingError("Choose no more than 10 files per cheatsheet.")

        if isinstance(entry, (str, Path)):
            path = Path(entry).expanduser()
            file_name = path.name
            if path.suffix.lower() not in {".pdf", ".docx", ".pptx"}:
                raise DocumentParsingError(f"{file_name}: choose a PDF, DOCX, or PPTX file.")
            with path.open("rb") as file:
                contents = file.read(MAX_FILE_SIZE + 1)
        else:
            if not isinstance(entry, (tuple, list)) or len(entry) != 2:
                raise TypeError("Use file paths, a filename-to-bytes mapping, or (filename, bytes) pairs.")
            file_name, contents = entry
            if not isinstance(file_name, str) or not isinstance(contents, bytes):
                raise TypeError("Each document must contain a filename string and bytes.")
            file_name = Path(file_name.replace("\\", "/")).name

        if Path(file_name).suffix.lower() not in {".pdf", ".docx", ".pptx"}:
            raise DocumentParsingError(f"{file_name}: choose a PDF, DOCX, or PPTX file.")
        if not contents or len(contents) > MAX_FILE_SIZE:
            raise DocumentParsingError(f"{file_name}: choose a nonempty file no larger than 25 MB.")

        total_size += len(contents)
        if total_size > MAX_TOTAL_FILE_SIZE:
            raise DocumentParsingError("Keep the combined file size at or below 100 MB.")
        documents.append((file_name, contents))

    if not documents:
        raise DocumentParsingError("Choose at least one lecture file.")
    return documents
