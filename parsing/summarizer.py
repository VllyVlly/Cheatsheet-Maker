from parsing.jsonformat import ExtractedItem, ProcessedItems
import ollama

PROMPT = """
You are summarizing lecture notes for an exam cheatsheet.

INPUT FORMAT
The input is a JSON object with one field, "items", containing a list of items
produced by a classifier. Each item has:
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
- Return a single JSON object with one field, "items", in exactly the same
  format as the input. Do not return a bare list, and do not add any text
  outside the JSON.
- Keep the same number of items, in the same order
- Keep id, type, and section unchanged for every item.
- Only `content` may change, and only for definition, example, and explanation items.
- Do not merge, split, add, or drop items.

The items to summarize will be provided in the user message
"""


def classify(text, extra_prompt="") -> list[ExtractedItem]:
    prompt = PROMPT + "\n" + extra_prompt
    response = ollama.chat(
        model='qwen3.5',
        messages=[
            {'role': 'system', 'content': prompt},   
            {'role': 'user',   'content': text},     
        ],
        format=ProcessedItems.model_json_schema(),
        options={'temperature': 0},
    )

    raw = response.message.content

    parsed = ProcessedItems.model_validate_json(raw)              
    return parsed.items         
