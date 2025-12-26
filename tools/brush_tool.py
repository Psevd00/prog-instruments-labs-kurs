7.	# tools/brush_tool.py
from tools.base_tool import BaseTool
from PIL import ImageDraw
import math
from typing import Tuple


class BrushTool(BaseTool):
    """Инструмент Кисть для рисования"""

    def __init__(self):
        super().__init__(name="Кисть", icon="🖌️")
        self.cursor = "circle"
        self.last_x = None
        self.last_y = None
        self.drawing = False
        self.size = 5
        self.color = (0, 0, 0, 255)
        self.pressure_sensitive = False  # Для плавности линий

    def on_mouse_down(self, event, model, canvas):
        # Сохраняем состояние перед началом рисования
        if hasattr(canvas, 'controller'):
            canvas.controller.save_state()

        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
        self._draw_point(event.x, event.y, model)

    def on_mouse_move(self, event, model, canvas):
        if self.drawing and self.last_x is not None and self.last_y is not None:
            # Рассчитываем расстояние между точками
            distance = math.sqrt((event.x - self.last_x) ** 2 + (event.y - self.last_y) ** 2)

            if distance > 0:
                # Адаптивный шаг в зависимости от скорости движения
                step = max(1, self.size // 3)
                steps = max(1, int(distance / step))

                for i in range(steps + 1):
                    t = i / steps
                    x = int(self.last_x + (event.x - self.last_x) * t)
                    y = int(self.last_y + (event.y - self.last_y) * t)
                    self._draw_point(x, y, model)

            self.last_x = event.x
            self.last_y = event.y
            canvas.update_image()

    def on_mouse_up(self, event, model, canvas):
        self.drawing = False
        self.last_x = None
        self.last_y = None
        model.modified = True
        canvas.update_image()

    def _draw_point(self, x: int, y: int, model):
        """Нарисовать одну точку/круг"""
        if 0 <= x < model.width and 0 <= y < model.height:
            draw = ImageDraw.Draw(model.image)
            if self.size == 1:
                draw.point((x, y), fill=self.color)
            else:
                radius = self.size // 2
                # Для лучшего качества рисуем эллипс
                draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                             fill=self.color, outline=self.color)

    def set_color(self, color: Tuple):
        self.color = color

    def set_size(self, size: int):
        if size > 0:
            self.size = size
