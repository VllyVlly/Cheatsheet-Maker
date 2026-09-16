from parsing.parser import ItemType, ExtractedItem

def assemble_latex(org_data):
    for section, contents in org_data.items():
        # write the section title
        for entry in contents:
            match entry.type:
                case ItemType.definition:
                    return
                case ItemType.example:
                    return
                case ItemType.formula:
                    return
                case ItemType.explanation:
                    return               