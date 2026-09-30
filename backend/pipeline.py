from latex.assembler import assemble_latex, compile_latex
from latex.settings import FormatSettings
from parsing.classifier import classify_gemini
from parsing.parser import organize_parsed, parse_pdf
from parsing.summarizer import summarizer_gemini


def generate_cheatsheet(client, file_bytes,
                        settings=FormatSettings(), output_name="cheatsheet", 
                        extra_classifier="", extra_summarizer=""):
    parsed = parse_pdf(file_bytes) 
    print("parsed chars:", len(parsed))  
    classified = classify_gemini(client, parsed, extra_prompt=extra_classifier)
    summarized = summarizer_gemini(client, classified, extra_prompt=extra_summarizer)
    organized = organize_parsed(summarized)
    latex = assemble_latex(organized, settings)
    pdf_path = compile_latex(latex, filename=output_name)
    if pdf_path is None:
        raise RuntimeError("LaTeX compilation failed")
    return pdf_path

