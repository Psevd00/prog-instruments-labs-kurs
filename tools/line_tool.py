11.	# tools/line_tool.py
from tools.base_tool import BaseTool
from PIL import Image, ImageDraw
import tkinter as tk
from typing import Tuple


class LineTool(BaseTool):
    """Инструмент для рисования линии"""

    def __init__(self):
        super().__init__(name="Линия", icon="📏")
        self.cursor = "crosshair"
        self.start_x = None
        self.start_y = None
        self.drawing = False
        self.color = (0, 0, 0, 255)
        self.line_width = 2
        self.preview_line = None

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
            if self.preview_line:
                canvas.delete(self.preview_line)

            # Рисуем новый предпросмотр на холсте
            self.preview_line = canvas.create_line(
                self.start_x, self.start_y, event.x, event.y,
                fill=self._rgb_to_hex(self.color),
                width=self.line_width,
                tags="preview"
            )

    def on_mouse_up(self, event, model, canvas):
        if self.drawing and self.start_x is not None and self.start_y is not None:
            self.drawing = False

            # Удаляем предпросмотр
            if self.preview_line:
                canvas.delete(self.preview_line)
                self.preview_line = None

            # Рисуем окончательную линию на изображении
            draw = ImageDraw.Draw(model.image)
            draw.line([(self.start_x, self.start_y), (event.x, event.y)],
                      fill=self.color,
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

    def set_line_width(self, width: int):
        self.line_width = max(1, width)
