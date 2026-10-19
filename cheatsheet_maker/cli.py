import argparse

from .maker import CheatsheetMaker
from .settings import FormatSettings


def main():
    parser = argparse.ArgumentParser(description="Combine lecture documents into a cheatsheet.")
    parser.add_argument("files", nargs="+", help="PDF, DOCX, or PPTX paths")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--output-name", default=None)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda", "mps"], default="auto")
    parser.add_argument("--model", default="gemini-3.6-flash")
    parser.add_argument("--columns", type=int, choices=[1, 2, 3, 4], default=2)
    parser.add_argument("--no-pdf", action="store_true", help="Write LaTeX without requiring Tectonic")
    options = parser.parse_args()

    try:
        with CheatsheetMaker(device=options.device, model=options.model) as maker:
            result = maker.generate(
                options.files,
                settings=FormatSettings(columns=options.columns),
                output_dir=options.output_dir,
                output_name=options.output_name,
                compile_pdf=not options.no_pdf,
            )
    except (ValueError, RuntimeError, OSError) as error:
        parser.exit(1, f"{error}\n")

    print(result.pdf_path or result.tex_path)
