6.	# tools/base_tool.py
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any


class BaseTool(ABC):
    """Абстрактный базовый класс для всех инструментов"""

    def __init__(self, name: str, icon: str = ""):
        self.name = name
        self.icon = icon
        self.active = False
        self.cursor = "arrow"

    @abstractmethod
    def on_mouse_down(self, event, model, canvas):
        pass

    @abstractmethod
    def on_mouse_move(self, event, model, canvas):
        pass

    @abstractmethod
    def on_mouse_up(self, event, model, canvas):
        pass

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def get_options_widget(self, parent):
        return None
