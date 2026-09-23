from flask import Flask, request
from flask_cors import CORS
from backend.pipeline import generate_cheatsheet, build_converter, build_liteparse
from parsing.parser import organize_parsed, parse, parse_liteparse
import parsing.classifier as classifier
import parsing.summarizer as summarizer

import os
from google import genai

app = Flask(__name__)
CORS(app)

# routes go here for now — you'll move them out later


@app.route("/generate_lite", methods=["POST"])
def generate_lite():
    file = request.files.get("file")
    if file is None:
        return {"error": "no file provided"}, 400
    contents = file.read()
    file_name = file.filename

    parser = build_liteparse()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    pdf_path = generate_cheatsheet(
        parse_liteparse, parser, client, contents, file_name,
        output_name="cheatsheet_lite",
        extra_classifier=classifier.CLASSIFIER_EXTRA,
        extra_summarizer=summarizer.SUMMARIZER_EXTRA,
    )
    return {"pdf_path": pdf_path}


@app.route("/generate_quality", methods=["POST"])
def generate_quality():
    file = request.files.get("file")
    if file is None:
        return {"error": "no file provided"}, 400
    contents = file.read()
    file_name = file.filename

    converter = build_converter()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    pdf_path = generate_cheatsheet(
        parse, converter, client, contents, file_name,
        output_name="cheatsheet_quality",
        extra_classifier=classifier.CLASSIFIER_EXTRA,
        extra_summarizer=summarizer.SUMMARIZER_EXTRA,
    )
    return {"pdf_path": pdf_path}



if __name__ == "__main__":
    app.run(debug=True)