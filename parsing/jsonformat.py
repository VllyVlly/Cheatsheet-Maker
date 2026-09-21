from enum import Enum
from pydantic import BaseModel, Field

class ItemType(str, Enum):
    definition = "definition"
    example = "example"
    formula = "formula"
    explanation = "explanation"
    theorem = "theorem"

class ExtractedItem(BaseModel):
    type: ItemType = Field(
        description=(
            "definition: defines a term or states a law/theorem. "
            "example: a worked example or problem. "
            "formula: a STANDALONE equation only, no full sentences; "
            "a sentence that contains math is NOT a formula. "
            "explanation: any other prose."
            """theorem: a formally stated, provable result: theorems, lemmas, propositions,
            corollaries. Include the conditions (assumptions) and the conclusion, but not
            the proof. A named law or principle without a proof (e.g. Newton's laws) is a
            definition, not a theorem."""
        )
    )
    content: str = Field(description=("the actual content of the parsed object"))
    section: str = Field(description=("the section the parsed object belongs to"))