from parsing.jsonformat import ItemType
from latex.settings import Orientation, FormatSettings

import subprocess

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
    result = []
    for char in text:
        result.append(replacements.get(char, char))
    return "".join(result)

def assemble_latex(org_data, settings: FormatSettings = FormatSettings()):
    lines = [
        r"\documentclass{article}",
        f"\\usepackage[margin={settings.margin}]{{geometry}}",
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
        lines.append(f"\\section{{{section}}}")
        for entry in contents:
            match entry.type:
                case ItemType.definition:
                    lines.append(f"\\textbf{{{escape_latex(entry.content)}}}")
                case ItemType.example:
                    lines.append(f"\\textit{{{escape_latex(entry.content)}}}")
                case ItemType.formula:
                    lines.append(f"${entry.content}$")
                case ItemType.explanation:
                    lines.append(escape_latex(entry.content))

    if settings.columns > 1:
        lines.append(r"\end{multicols}")
    lines.append(r"\end{document}")
    return "\n".join(lines)


def compile_latex(tex_content, output_dir="output", filename="cheatsheet"):
    tex_path = f"{output_dir}/{filename}.tex"
    with open(tex_path, "w") as f:
        f.write(tex_content)

    result = subprocess.run(
        ["tectonic", tex_path],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Compilation failed:")
        print(result.stderr)
        return None

    return f"{output_dir}/{filename}.pdf"