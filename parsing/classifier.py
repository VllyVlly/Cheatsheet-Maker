from parsing.jsonformat import ExtractedItem
import google
import time

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

EXAMPLES
Input: "The force FBA exerted by object B on object A equals FAB in magnitude"
Output: type=explanation,
content="The force $F_{BA}$ exerted by object B on object A equals $F_{AB}$ in magnitude"

Input: "$$F_{net} = ma$$" (standalone equation)
Output: type=formula, content="F_{net} = ma"

Input: "The acceleration is proportional to the net force, so F_net = ma."
Output: type=explanation,
content="The acceleration is proportional to the net force, so $F_{net} = ma$."
(This is prose containing math, so it is NOT a formula.)

Now extract and classify the following lecture material: """


def classify(client, md, model="gemini-3.6-flash", max_retries=4):
    prompt = PROMPT + "\n'\n" + md
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
