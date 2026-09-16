from enum import Enum
from pydantic import BaseModel

class ItemType(str, Enum):
    definition = "definition"
    example = "example"
    formula = "formula"
    explanation = "explanation"

class ExtractedItem(BaseModel):
    type: ItemType
    content: str
    section: str