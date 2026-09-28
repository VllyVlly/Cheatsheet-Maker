import os
import sys
from google import genai
from backend.pipeline import generate_cheatsheet

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