from latex.assembler import assemble_latex, compile_latex
from latex.settings import FormatSettings
from parsing.classifier import classify
from parsing.parser import organize_parsed, parse_pdf
from parsing.summarizer import summarizer


def generate_cheatsheet(file_bytes,
                        settings=FormatSettings(), output_name="cheatsheet", 
                        extra_classifier="", extra_summarizer=""):
    parsed = parse_pdf(file_bytes) 
    print("parsed chars:", len(parsed))  
    classified = classify(parsed, extra_prompt=extra_classifier)
    summarized = summarizer(classified, extra_prompt=extra_summarizer)
    organized = organize_parsed(summarized)
    latex = assemble_latex(organized, settings)
    pdf_path = compile_latex(latex, filename=output_name)
    if pdf_path is None:
        raise RuntimeError("LaTeX compilation failed")
    return pdf_path

