12.	# tools/pipette_tool.py
from tools.base_tool import BaseTool
from typing import Tuple, Optional


class PipetteTool(BaseTool):
    """Инструмент Пипетка для выбора цвета"""

    def __init__(self):
        super().__init__(name="Пипетка", icon="🔍")
        self.cursor = "crosshair"

    def on_mouse_down(self, event, model, canvas):
        self._pick_color(event.x, event.y, model, canvas)

    def on_mouse_move(self, event, model, canvas):
        pass

    def on_mouse_up(self, event, model, canvas):
        pass

    def _pick_color(self, x: int, y: int, model, canvas):
        if 0 <= x < model.width and 0 <= y < model.height:
            color = model.image.getpixel((x, y))

            if len(color) == 4:
                rgb_color = color[:3] + (255,)
            else:
                rgb_color = color + (255,)

            if hasattr(canvas, 'controller') and hasattr(canvas.controller, 'view'):
                canvas.controller.view.set_color(rgb_color)

            return color

        return None
