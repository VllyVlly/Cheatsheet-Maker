from parsing.jsonformat import ExtractedItem
import google
import time

def classify(client, md, model="gemini-3.6-flash", max_retries=4):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=f"""Extract and classify content from this lecture material into structured items.

                When writing the `content` field for each item, wrap any mathematical notation in LaTeX 
                inline-math delimiters ($...$) — this includes variables, subscripts, superscripts, and 
                equations, even short ones like a single variable with a subscript. Do not wrap plain 
                prose text that has no mathematical meaning.

                Example:
                Input text: "The force FBA exerted by object B on object A equals FAB in magnitude"
                Correct content field: "The force $F_{{BA}}$ exerted by object B on object A equals $F_{{AB}}$ in magnitude"

                The lecture material may already contain some math wrapped in $...$ or $$...$$ 
                delimiters (e.g. from formula extraction). Leave any already-delimited math 
                exactly as it is — do not add extra delimiters or change inline ($...$) to 
                display ($$...$$) or vice versa. Only add $...$ delimiters to mathematical 
                notation that appears as plain, undelimited text.

                Now extract and classify the following lecture material:
                \n\n{md}""",
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[ExtractedItem],
                },
            )
            return response.parsed
        except google.genai.errors.ServerError as e:
            wait = 2 ** attempt
            print(f"Gemini overloaded (attempt {attempt+1}/{max_retries}), retrying in {wait}s...")
            time.sleep(wait)

    print(f"classify() failed after {max_retries} attempts, returning None")
    return None
