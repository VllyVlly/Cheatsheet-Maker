from pydantic import BaseModel
from enum import Enum

# Enums
class Orientation(str, Enum):
    portrait = "portrait"
    landscape = "landscape"

# Settings 
class FormatSettings(BaseModel):
    font_size: str = "footnotesize"
    columns: int = 2
    orientation: Orientation = Orientation.portrait
    margin: str = "1in"

# Unused rn
class FileSettings(BaseModel):
    file_name: str = "cheatsheet"