# utils/constants.py
from enum import Enum

class ToolMode(Enum):
    BRUSH = "brush"
    ERASER = "eraser"
    FILL = "fill"
    SELECTION = "selection"
    PIPETTE = "pipette"
    TEXT = "text"

# Цвета по умолчанию
DEFAULT_BG_COLOR = (255, 255, 255, 255)  # Белый
DEFAULT_FG_COLOR = (0, 0, 0, 255)        # Чёрный