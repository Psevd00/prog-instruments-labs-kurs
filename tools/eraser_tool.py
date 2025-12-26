9.	# tools/eraser_tool.py
from tools.base_tool import BaseTool
from PIL import ImageDraw
import math
from typing import Tuple


class EraserTool(BaseTool):
    """Инструмент Ластик для стирания"""

    def __init__(self):
        super().__init__(name="Ластик", icon="🧽")
        self.cursor = "circle"
        self.last_x = None
        self.last_y = None
        self.drawing = False
        self.size = 10
        self.eraser_color = (255, 255, 255, 255)

    def on_mouse_down(self, event, model, canvas):
        # Сохраняем состояние перед началом стирания
        if hasattr(canvas, 'controller'):
            canvas.controller.save_state()

        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
        self._erase_point(event.x, event.y, model)

    def on_mouse_move(self, event, model, canvas):
        if self.drawing and self.last_x is not None and self.last_y is not None:
            self._erase_smooth_line(self.last_x, self.last_y,
                                    event.x, event.y, model)
            self.last_x = event.x
            self.last_y = event.y

    def on_mouse_up(self, event, model, canvas):
        self.drawing = False
        self.last_x = None
        self.last_y = None
        model.modified = True

    def _erase_point(self, x: int, y: int, model):
        """Стереть одну точку/круг"""
        if 0 <= x < model.width and 0 <= y < model.height:
            draw = ImageDraw.Draw(model.image)
            if self.size == 1:
                draw.point((x, y), fill=self.eraser_color)
            else:
                radius = self.size // 2
                draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                             fill=self.eraser_color)

    def _erase_smooth_line(self, x1: int, y1: int, x2: int, y2: int, model):
        """Стереть плавную линию из перекрывающихся кругов"""
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            self._erase_point(x1, y1, model)
            return

        step = max(1, self.size // 2)
        num_steps = int(distance / step) + 1

        for i in range(num_steps + 1):
            t = i / num_steps if num_steps > 0 else 0
            x = int(x1 + dx * t)
            y = int(y1 + dy * t)
            self._erase_point(x, y, model)

    def set_size(self, size: int):
        if size > 0:
            self.size = size
