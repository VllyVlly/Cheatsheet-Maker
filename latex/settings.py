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

    def __init__(self, font_size, columns, orientation, margin):
        self.font_size = font_size
        self.columns = columns
        self.orientation = orientation
        self.margin = margin
