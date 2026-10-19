from ..parsing.jsonformat import ItemType
from ..settings import Orientation, FormatSettings

import subprocess
import re
import os
import shutil
from pathlib import Path

def escape_latex(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    split = re.split(r'(\$[^$]*\$)', text)
    result = []
    for entry in split:
        if entry.startswith("$") and entry.endswith("$"):
            result.append(entry)
        else:
            for char in entry:
                result.append(replacements.get(char, char))
    return "".join(result)

def assemble_latex(org_data, settings: FormatSettings = FormatSettings()):
    lines = [
        r"\documentclass{article}",
        f"\\usepackage[margin={settings.margin},{settings.orientation.value}]{{geometry}}",
        r"\usepackage{amsmath}",
    ]
    if settings.orientation == Orientation.landscape:
        lines.append(r"\usepackage{pdflscape}")
    if settings.columns > 1:
        lines.append(r"\usepackage{multicol}")


    lines.append(r"\begin{document}")
    lines.append(f"\\{settings.font_size}")
    if settings.columns > 1:
        lines.append(r"\raggedcolumns")
        lines.append(f"\\begin{{multicols}}{{{settings.columns}}}")

    for section, contents in org_data.items():
        lines.append(f"\\section{{{escape_latex(section)}}}")
        for entry in contents:
            match entry.type:
                case ItemType.definition:
                    lines.append(f"\\textbf{{{escape_latex(entry.content)}}}")
                    lines.append("") 
                case ItemType.example:
                    lines.append(f"\\textit{{{escape_latex(entry.content)}}}")
                    lines.append("") 
                case ItemType.formula:
                    lines.append(f"${entry.content}$")
                    lines.append("") 
                case ItemType.explanation:
                    lines.append(escape_latex(entry.content))
                    lines.append("") 
                case ItemType.theorem:
                    lines.append(f"\\textbf{{{escape_latex(entry.content)}}}")
                    lines.append("") 

    if settings.columns > 1:
        lines.append(r"\end{multicols}")
    lines.append(r"\end{document}")
    return "\n".join(lines)


def compile_latex(tex_content, output_dir="output", filename="cheatsheet", timeout=120):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", filename):
        raise ValueError("Use a plain output name without a path or file extension.")
    executable = shutil.which("tectonic")
    if executable is None:
        raise FileNotFoundError("Install Tectonic on PATH to compile a PDF, or use compile_pdf=False to generate LaTeX only.")

    output_directory = Path(output_dir).resolve()
    output_directory.mkdir(parents=True, exist_ok=True)
    tex_path = output_directory / f"{filename}.tex"
    tex_path.write_text(tex_content, encoding="utf-8")

    environment_names = {
        "PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "HOME", "USERPROFILE",
        "LOCALAPPDATA", "APPDATA", "XDG_CACHE_HOME", "SSL_CERT_FILE", "SSL_CERT_DIR",
        "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "no_proxy",
    }
    environment = {name: value for name, value in os.environ.items() if name.upper() in environment_names or name in environment_names}
    environment["TECTONIC_UNTRUSTED_MODE"] = "1"

    try:
        result = subprocess.run(
            [executable, "-X", "compile", "--untrusted", "--outdir", str(output_directory), str(tex_path)],
            cwd=output_directory,
            env=environment,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"LaTeX compilation exceeded {timeout} seconds. The .tex source is available in the output directory.") from error

    pdf_path = output_directory / f"{filename}.pdf"
    if result.returncode != 0 or not pdf_path.is_file():
        raise RuntimeError("LaTeX compilation failed. Review the generated .tex source or generate with compile_pdf=False.")
    return str(pdf_path)
