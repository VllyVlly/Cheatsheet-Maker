from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Literal
import re

# Enums
class Orientation(str, Enum):
    portrait = "portrait"
    landscape = "landscape"

# Settings 
class FormatSettings(BaseModel):
    font_size: Literal["tiny", "scriptsize", "footnotesize", "small", "normalsize"] = "footnotesize"
    columns: int = Field(default=2, ge=1, le=4)
    orientation: Orientation = Orientation.portrait
    margin: str = "1in"

    @field_validator("margin")
    @classmethod
    def validate_margin(cls, value):
        match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)(in|cm|mm|pt)", value)
        if match is None or float(match.group(1)) <= 0:
            raise ValueError("Margin must be a positive measurement such as 1in")
        return value

# Unused rn
class FileSettings(BaseModel):
    file_name: str = "cheatsheet"
