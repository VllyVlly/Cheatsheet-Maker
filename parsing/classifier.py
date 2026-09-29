from parsing.jsonformat import ExtractedItem, ProcessedItems
import ollama

PROMPT = """
Extract and classify content from the lecture material below into structured items.
Each item has: type, content, section.

ITEM TYPES
- definition: a statement that defines a term, or states a named law or principle.
- example: a worked example, problem, or illustration.
- formula: a STANDALONE equation or expression only. It must contain no full
sentences. A sentence that merely contains math is NOT a formula.
- explanation: any other prose, including sentences that contain math.
- theorem: a formally stated, provable result: theorems, lemmas, propositions,
corollaries. Include the conditions and the conclusion, but not the proof.
A named law or principle without a proof (e.g. Newton's laws) is a definition.

MATH RULES
1. formula items: write raw LaTeX math only. Do NOT include any $ or $$
delimiters, even if the source has them. Remove them.
2. definition, theorem, example, explanation items: wrap every piece of math in
inline delimiters $...$. This includes variables, subscripts, superscripts,
and short equations, even a single variable like $m$.
Leave plain words without math meaning undelimited.
3. If the source already has $...$ or $$...$$ inside prose, keep that math
as it is. Do not add extra delimiters or change inline to display.

OUTPUT FORMAT
Return a single JSON object with one field, "items", containing the list of
extracted items. Each item has "type", "content", and "section". Do not return
a bare list, and do not add any text outside the JSON.

EXAMPLES
Input: "The force FBA exerted by object B on object A equals FAB in magnitude"
Output: {"items": [{"type": "explanation",
"content": "The force $F_{BA}$ exerted by object B on object A equals $F_{AB}$ in magnitude",
"section": "Newton's Third Law"}]}

Input: "$$F_{net} = ma$$" (standalone equation)
Output: {"items": [{"type": "formula",
"content": "F_{net} = ma",
"section": "Newton's Second Law"}]}

Input: "The acceleration is proportional to the net force, so F_net = ma."
Output: {"items": [{"type": "explanation",
"content": "The acceleration is proportional to the net force, so $F_{net} = ma$.",
"section": "Newton's Second Law"}]}
(This is prose containing math, so it is NOT a formula.)

Return your answer as a single JSON object with one field, "items",
containing the list of extracted items. Do not return a bare list,
and do not add any text outside the JSON.

The lecture material to process will be provided in the user message.
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
