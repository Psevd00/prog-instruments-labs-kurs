# tools/pipette_tool.py
from tools.base_tool import BaseTool
from typing import Tuple, Optional


class PipetteTool(BaseTool):
    """Инструмент Пипетка для выбора цвета"""

    def __init__(self):
        super().__init__(name="Пипетка", icon="🔍")
        self.cursor = "crosshair"

    def on_mouse_down(self, event, model, canvas):
        """Выбор цвета при клике"""
        self._pick_color(event.x, event.y, model, canvas)

    def on_mouse_move(self, event, model, canvas):
        """Показываем цвет под курсором"""
        # Можно добавить превью цвета при перемещении
        pass

    def on_mouse_up(self, event, model, canvas):
        """Ничего не делаем при отпускании"""
        pass

    def _pick_color(self, x: int, y: int, model, canvas):
        """Выбрать цвет из пикселя"""
        if 0 <= x < model.width and 0 <= y < model.height:
            color = model.image.getpixel((x, y))

            # Преобразуем в формат RGB (убираем альфа-канал если нужно)
            if len(color) == 4:
                rgb_color = color[:3] + (255,)  # Сохраняем альфа-канал
            else:
                rgb_color = color + (255,)

            # Устанавливаем цвет в главном окне
            if hasattr(canvas, 'controller') and hasattr(canvas.controller, 'view'):
                canvas.controller.view.set_color(rgb_color)

            return color

        return None