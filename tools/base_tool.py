# tools/base_tool.py
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
        """Обработчик нажатия кнопки мыши"""
        pass

    @abstractmethod
    def on_mouse_move(self, event, model, canvas):
        """Обработчик перемещения мыши"""
        pass

    @abstractmethod
    def on_mouse_up(self, event, model, canvas):
        """Обработчик отпускания кнопки мыши"""
        pass

    def activate(self):
        """Активировать инструмент"""
        self.active = True

    def deactivate(self):
        """Деактивировать инструмент"""
        self.active = False

    def get_options_widget(self, parent):
        """Вернуть виджет настроек инструмента (опционально)"""
        return None