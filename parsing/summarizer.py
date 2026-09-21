from parsing.jsonformat import ExtractedItem
import google
import time
import json

PROMPT = """
You are summarizing lecture notes for an exam cheatsheet.

INPUT FORMAT
The input is a JSON array of items produced by a classifier. Each item has:
- type: one of definition, theorem, example, formula, explanation.
- content: the text of the item. Math is written in LaTeX.
- section: the heading the item belongs to.

TASK
For items of type definition, example, and explanation:
- Rewrite `content` as a shorter version that keeps the key idea.
- Each sentence must be at most 20 words.
- Remove filler and repetition. Do not add information that is not in the original.

For items of type formula and theorem:
- Return them exactly as given. Do not change them at all.

MATH RULES
- Math wrapped in $...$ inside content must be copied exactly as it is.
- Do not edit, reformat, add, or remove any math or its $ delimiters.
- Only change the words around the math.

OUTPUT FORMAT
- Return a JSON array in exactly the same format as the input.
- Keep the same number of items, in the same order.
- Keep id, type, and section unchanged for every item.
- Only `content` may change, and only for definition, example, and explanation items.
- Do not merge, split, add, or drop items.

Now summarize the following items:
"""


def summarizer(client, items, model="gemini-3.6-flash", max_retries=4):
    text = json.dumps([item.model_dump(mode="json") for item in items], ensure_ascii=False)
    prompt = PROMPT + "\n'\n" + text
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
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
