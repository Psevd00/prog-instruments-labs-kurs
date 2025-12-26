8.	# tools/ellipse_tool.py
from tools.base_tool import BaseTool
from PIL import ImageDraw
import tkinter as tk
from typing import Tuple


class EllipseTool(BaseTool):
    """Инструмент для рисования эллипса/окружности"""

    def __init__(self):
        super().__init__(name="Эллипс", icon="⭕")
        self.cursor = "crosshair"
        self.start_x = None
        self.start_y = None
        self.drawing = False
        self.color = (0, 0, 0, 255)
        self.fill = False
        self.fill_color = (0, 0, 0, 255)
        self.line_width = 2
        self.preview_ellipse = None

    def on_mouse_down(self, event, model, canvas):
        # Сохраняем состояние перед началом рисования
        if hasattr(canvas, 'controller'):
            canvas.controller.save_state()

        self.drawing = True
        self.start_x = event.x
        self.start_y = event.y

    def on_mouse_move(self, event, model, canvas):
        if self.drawing and self.start_x is not None and self.start_y is not None:
            # Удаляем старый предпросмотр
            if self.preview_ellipse:
                canvas.delete(self.preview_ellipse)

            # Нормализуем координаты
            x1 = min(self.start_x, event.x)
            y1 = min(self.start_y, event.y)
            x2 = max(self.start_x, event.x)
            y2 = max(self.start_y, event.y)

            # Рисуем новый предпросмотр на холсте
            if self.fill:
                self.preview_ellipse = canvas.create_oval(
                    x1, y1, x2, y2,
                    fill=self._rgb_to_hex(self.fill_color),
                    outline=self._rgb_to_hex(self.color),
                    width=self.line_width,
                    tags="preview"
                )
            else:
                self.preview_ellipse = canvas.create_oval(
                    x1, y1, x2, y2,
                    outline=self._rgb_to_hex(self.color),
                    width=self.line_width,
                    tags="preview"
                )

    def on_mouse_up(self, event, model, canvas):
        if self.drawing and self.start_x is not None and self.start_y is not None:
            self.drawing = False

            # Удаляем предпросмотр
            if self.preview_ellipse:
                canvas.delete(self.preview_ellipse)
                self.preview_ellipse = None

            # Нормализуем координаты
            x1 = min(self.start_x, event.x)
            y1 = min(self.start_y, event.y)
            x2 = max(self.start_x, event.x)
            y2 = max(self.start_y, event.y)

            # Рисуем окончательный эллипс на изображении
            draw = ImageDraw.Draw(model.image)

            if self.fill:
                draw.ellipse([(x1, y1), (x2, y2)],
                             fill=self.fill_color,
                             outline=self.color,
                             width=self.line_width)
            else:
                draw.ellipse([(x1, y1), (x2, y2)],
                             outline=self.color,
                             width=self.line_width)

            model.modified = True

            # Обновляем холст
            canvas.update_image()

            self.start_x = None
            self.start_y = None

    def _rgb_to_hex(self, rgb):
        """Конвертировать RGB в HEX"""
        if len(rgb) >= 3:
            return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
        else:
            return '#000000'

    def set_color(self, color: Tuple):
        self.color = color

    def set_fill_color(self, color: Tuple):
        self.fill_color = color

    def set_line_width(self, width: int):
        self.line_width = max(1, width)

    def set_fill(self, fill: bool):
        self.fill = fill
