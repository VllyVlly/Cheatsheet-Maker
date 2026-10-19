from cheatsheet_maker import CheatsheetMaker


def generate_cheatsheet(client, file_bytes, settings=None, output_name="cheatsheet",
                        extra_classifier="", extra_summarizer="", output_dir="output"):
    documents = [("lecture.pdf", file_bytes)] if isinstance(file_bytes, bytes) else file_bytes
    with CheatsheetMaker(client=client) as maker:
        result = maker.generate(
            documents,
            settings=settings,
            output_dir=output_dir,
            output_name=output_name,
            extra_classifier=extra_classifier,
            extra_summarizer=extra_summarizer,
        )
    return str(result.pdf_path)
