15.	# tools/shape_tool.py
from tools.base_tool import BaseTool
from PIL import Image, ImageDraw
from typing import Tuple, Optional


class ShapeTool(BaseTool):
    """Базовый класс для геометрических примитивов"""

    def __init__(self, name: str, icon: str = ""):
        super().__init__(name, icon)
        self.cursor = "crosshair"
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.drawing = False
        self.color = (0, 0, 0, 255)
        self.fill = False
        self.fill_color = (0, 0, 0, 255)
        self.line_width = 2

    def on_mouse_down(self, event, model, canvas):
        # Сохраняем состояние перед началом рисования
        if hasattr(canvas, 'controller'):
            canvas.controller.save_state()

        self.drawing = True
        self.start_x = event.x
        self.start_y = event.y
        self.current_x = event.x
        self.current_y = event.y

    def on_mouse_move(self, event, model, canvas):
        if self.drawing:
            self.current_x = event.x
            self.current_y = event.y

            # Создаем временное изображение для предпросмотра
            temp_image = model.image.copy()
            draw = ImageDraw.Draw(temp_image)

            # Рисуем предпросмотр фигуры
            x1, y1, x2, y2 = self._normalize_coords(
                self.start_x, self.start_y,
                self.current_x, self.current_y
            )

            # Рисуем фигуру на временном изображении
            self._draw_preview(draw, x1, y1, x2, y2)

            # Временно заменяем изображение для предпросмотра
            original_image = model.image
            model._image = temp_image
            canvas.update_image()

            # Восстанавливаем оригинальное изображение
            model._image = original_image

    def on_mouse_up(self, event, model, canvas):
        if self.drawing:
            self.drawing = False
            self.current_x = event.x
            self.current_y = event.y

            if self.start_x is not None and self.start_y is not None:
                # Нормализуем координаты
                x1, y1, x2, y2 = self._normalize_coords(
                    self.start_x, self.start_y,
                    self.current_x, self.current_y
                )

                # Рисуем фигуру на изображении
                self._draw_shape(model, x1, y1, x2, y2)

                self.start_x = None
                self.start_y = None
                self.current_x = None
                self.current_y = None

                model.modified = True

                # Обновляем холст
                canvas.update_image()

    def _normalize_coords(self, x1, y1, x2, y2) -> Tuple:
        """Нормализовать координаты (делаем x1 <= x2 и y1 <= y2)"""
        # Для линии НЕ нормализуем, потому что это меняет направление
        # Для прямоугольника и эллипса - нормализуем
        if self.__class__.__name__ in ['LineTool']:
            return (x1, y1, x2, y2)
        else:
            return (
                min(x1, x2),
                min(y1, y2),
                max(x1, x2),
                max(y1, y2)
            )

    def _draw_shape(self, model, x1: int, y1: int, x2: int, y2: int):
        """Абстрактный метод - должен быть переопределен в дочерних классах"""
        pass

    def _draw_preview(self, draw, x1: int, y1: int, x2: int, y2: int):
        """Метод для рисования предпросмотра"""
        pass

    def set_color(self, color: Tuple):
        self.color = color

    def set_fill_color(self, color: Tuple):
        self.fill_color = color

    def set_line_width(self, width: int):
        self.line_width = max(1, width)

    def set_fill(self, fill: bool):
        self.fill = fill
