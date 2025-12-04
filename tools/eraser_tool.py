# tools/eraser_tool.py
from tools.base_tool import BaseTool
from PIL import ImageDraw
from typing import Tuple


class EraserTool(BaseTool):
    """Инструмент Ластик для стирания"""

    def __init__(self):
        super().__init__(name="Ластик", icon="🧽")
        self.cursor = "circle"
        self.last_x = None
        self.last_y = None
        self.drawing = False

        # Параметры ластика
        self.size = 10
        self.eraser_color = (255, 255, 255, 255)  # Белый цвет ластика

    def on_mouse_down(self, event, model, canvas):
        """Начало стирания"""
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y

        # Стираем первую точку
        self._erase_point(event.x, event.y, model)

    def on_mouse_move(self, event, model, canvas):
        """Стирание при перемещении мыши"""
        if self.drawing and self.last_x is not None and self.last_y is not None:
            # Стираем линию от предыдущей точки к текущей
            self._erase_line(self.last_x, self.last_y, event.x, event.y, model)
            self.last_x = event.x
            self.last_y = event.y

    def on_mouse_up(self, event, model, canvas):
        """Конец стирания"""
        self.drawing = False
        self.last_x = None
        self.last_y = None

        # Помечаем изображение как измененное
        model.modified = True

    def _erase_point(self, x: int, y: int, model):
        """Стереть точку"""
        if 0 <= x < model.width and 0 <= y < model.height:
            draw = ImageDraw.Draw(model.image)
            if self.size == 1:
                draw.point((x, y), fill=self.eraser_color)
            else:
                radius = self.size // 2
                draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                             fill=self.eraser_color)

    def _erase_line(self, x1: int, y1: int, x2: int, y2: int, model):
        """Стереть линию"""
        draw = ImageDraw.Draw(model.image)
        if self.size == 1:
            draw.line([(x1, y1), (x2, y2)], fill=self.eraser_color, width=1)
        else:
            # Для толстых ластиков стираем несколько точек вдоль линии
            draw.line([(x1, y1), (x2, y2)], fill=self.eraser_color, width=self.size)

    def set_size(self, size: int):
        """Установить размер ластика"""
        if size > 0:
            self.size = size