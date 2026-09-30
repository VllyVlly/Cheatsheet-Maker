import sys
from backend.pipeline import generate_cheatsheet
import os
from google import genai

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <lecture.pdf>")
        return

    path = sys.argv[1]
    with open(path, "rb") as f:
        file_bytes = f.read()

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    pdf_path = generate_cheatsheet(client, file_bytes, output_name="cheatsheet")
    print(f"Done: {pdf_path}")


if __name__ == "__main__":
    main()