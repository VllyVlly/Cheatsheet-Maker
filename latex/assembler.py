from parsing.jsonformat import ItemType

def assemble_latex(org_data):
    lines = [r"\documentclass{article}", r"\begin{document}"]
    for section, contents in org_data.items():
        lines.append(f"\\section{{{section}}}")
        for entry in contents:
            match entry.type:
                case ItemType.definition:
                    lines.append(f"\\textbf{{{entry.content}}}")
                case ItemType.example:
                    lines.append(f"\\textit{{{entry.content}}}")
                case ItemType.formula:
                    lines.append(f"${entry.content}$")
                case ItemType.explanation:
                    lines.append(entry.content)
    
    lines.append(r"\end{document}")
    return "\n".join(lines)