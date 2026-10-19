import os
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from .inputs import load_documents
from .latex.assembler import assemble_latex, compile_latex
from .parsing.classifier import classify_gemini
from .parsing.jsonformat import ExtractedItem
from .parsing.parser import organize_parsed, parse_files
from .parsing.summarizer import summarizer_gemini
from .settings import FormatSettings


@dataclass(frozen=True)
class CheatsheetResult:
    tex_path: Path
    pdf_path: Path | None
    markdown: str
    items: list[ExtractedItem]


class CheatsheetMaker:
    def __init__(self, api_key=None, *, client=None, model="gemini-3.6-flash",
                 device="auto", ocr=True, formula_enrichment=True, compile_timeout=120):
        if device not in {"auto", "cpu", "cuda", "mps"}:
            raise ValueError("Device must be auto, cpu, cuda, or mps.")
        if not isinstance(compile_timeout, (int, float)) or not 0 < compile_timeout < float("inf"):
            raise ValueError("Compilation timeout must be a positive, finite number.")
        if not isinstance(model, str) or not model.strip():
            raise ValueError("Choose a Gemini model name.")

        self._api_key = api_key
        self._client = client
        self._owns_client = client is None
        self._model = model
        self._device = device
        self._ocr = ocr
        self._formula_enrichment = formula_enrichment
        self._compile_timeout = compile_timeout
        self._converters = {}

    def parse(self, files):
        """Extract Markdown from paths, uploaded bytes, or filename/bytes pairs."""
        documents = load_documents(files)
        return parse_files(
            documents,
            converters=self._converters,
            device=self._device,
            ocr=self._ocr,
            formula_enrichment=self._formula_enrichment,
        )

    def generate(self, files, *, settings=None, output_dir="output", output_name=None,
                 extra_classifier="", extra_summarizer="", compile_pdf=True):
        self._get_client()
        markdown = self.parse(files)
        return self.generate_from_markdown(
            markdown,
            settings=settings,
            output_dir=output_dir,
            output_name=output_name,
            extra_classifier=extra_classifier,
            extra_summarizer=extra_summarizer,
            compile_pdf=compile_pdf,
        )

    def generate_from_markdown(self, markdown, *, settings=None, output_dir="output", output_name=None,
                               extra_classifier="", extra_summarizer="", compile_pdf=True):
        """Generate from saved Markdown without repeating document extraction."""
        if not isinstance(markdown, str) or not markdown.strip():
            raise ValueError("Provide nonempty Markdown to generate a cheatsheet.")
        output_name = output_name or uuid4().hex
        if not isinstance(output_name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", output_name):
            raise ValueError("Output name must contain 1–80 letters, numbers, underscores, or hyphens.")
        if settings is None:
            settings = FormatSettings()
        elif not isinstance(settings, FormatSettings):
            settings = FormatSettings.model_validate(settings)
        if not isinstance(extra_classifier, str) or not isinstance(extra_summarizer, str):
            raise TypeError("Custom prompts must be strings.")
        if max(len(extra_classifier), len(extra_summarizer)) > 10000:
            raise ValueError("Keep each custom prompt under 10,000 characters.")

        client = self._get_client()
        classified = classify_gemini(client, markdown, model=self._model, extra_prompt=extra_classifier)
        summarized = summarizer_gemini(client, classified, model=self._model, extra_prompt=extra_summarizer)
        latex = assemble_latex(organize_parsed(summarized), settings)

        output_directory = Path(output_dir).expanduser().resolve()
        output_directory.mkdir(parents=True, exist_ok=True)
        tex_path = output_directory / f"{output_name}.tex"
        tex_path.write_text(latex, encoding="utf-8")
        pdf_path = None
        if compile_pdf:
            pdf_path = Path(compile_latex(
                latex,
                output_dir=output_directory,
                filename=output_name,
                timeout=self._compile_timeout,
            ))

        return CheatsheetResult(tex_path, pdf_path, markdown, summarized)

    def _get_client(self):
        if self._client is None:
            api_key = self._api_key or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("Provide your own Gemini API key or set GEMINI_API_KEY. Parsing alone does not require a key.")
            from google import genai

            self._client = genai.Client(api_key=api_key)
        return self._client

    def close(self):
        if self._owns_client and self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback):
        self.close()
