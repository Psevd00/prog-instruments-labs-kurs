# tools/selection_tool.py
from tools.base_tool import BaseTool
from PIL import Image, ImageDraw
import tkinter as tk
from typing import Optional, Tuple


class SelectionTool(BaseTool):
    """Инструмент для прямоугольного выделения области"""

    def __init__(self):
        super().__init__(name="Выделение", icon="▢")
        self.cursor = "crosshair"

        # Координаты выделения
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.dragging = False
        self.moving = False

        # Визуальное представление выделения на холсте
        self.selection_rect = None
        self.selection_image = None
        self.offset_x = 0
        self.offset_y = 0

    def on_mouse_down(self, event, model, canvas):
        """Начало выделения или перемещения"""
        x, y = event.x, event.y

        if self._is_inside_selection(x, y) and model.selection:
            # Начало перемещения выделенной области
            self.moving = True
            self.offset_x = x - model.selection[0]
            self.offset_y = y - model.selection[1]
        else:
            # Начало нового выделения
            self.dragging = True
            self.start_x = x
            self.start_y = y
            self.end_x = x
            self.end_y = y
            model.set_selection(None)

            # Создаем прямоугольник выделения на холсте
            self._update_selection_rect(canvas)

    def on_mouse_move(self, event, model, canvas):
        """Изменение выделения или перемещение"""
        x, y = event.x, event.y

        if self.moving and model.selection and self.selection_image:
            # Перемещение выделенной области
            self._move_selection(x - self.offset_x, y - self.offset_y, model, canvas)

        elif self.dragging:
            # Изменение размера выделения
            self.end_x = x
            self.end_y = y
            self._update_selection_rect(canvas)

    def on_mouse_up(self, event, model, canvas):
        """Завершение выделения или перемещения"""
        x, y = event.x, event.y

        if self.dragging:
            # Завершение выделения
            self.dragging = False
            self.end_x = x
            self.end_y = y

            # Нормализуем координаты (делаем x1 < x2, y1 < y2)
            x1, y1, x2, y2 = self._normalize_coords()

            # Проверяем, что выделение не нулевое
            if abs(x2 - x1) > 1 and abs(y2 - y1) > 1:
                # Сохраняем выделение в модели
                model.set_selection((x1, y1, x2, y2))

                # Получаем изображение выделенной области
                self.selection_image = model.get_selection_image()
            else:
                model.set_selection(None)
                self.selection_image = None

            # Обновляем прямоугольник выделения
            self._update_selection_rect(canvas)

        elif self.moving:
            # Завершение перемещения
            self.moving = False

            if model.selection and self.selection_image:
                # Фиксируем новое положение выделения
                x1, y1, x2, y2 = model.selection
                width = x2 - x1
                height = y2 - y1

                new_x1 = max(0, min(x, model.width - width))
                new_y1 = max(0, min(y, model.height - height))
                new_x2 = new_x1 + width
                new_y2 = new_y1 + height

                model.set_selection((new_x1, new_y1, new_x2, new_y2))
                model.modified = True

            # Обновляем изображение
            canvas.update_image()

        # Сбрасываем временные координаты
        self.start_x = None
        self.start_y = None

    def _normalize_coords(self) -> Tuple:
        """Нормализовать координаты прямоугольника"""
        if self.start_x is None or self.start_y is None:
            return (0, 0, 0, 0)

        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)

        return (x1, y1, x2, y2)

    def _update_selection_rect(self, canvas):
        """Обновить визуальное отображение выделения на холсте"""
        # Удаляем старый прямоугольник
        if self.selection_rect:
            canvas.delete(self.selection_rect)

        # Создаем новый прямоугольник, если есть выделение
        if self.start_x is not None and self.end_x is not None:
            x1, y1, x2, y2 = self._normalize_coords()

            # Рисуем пунктирный прямоугольник
            self.selection_rect = canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='blue',
                dash=(4, 2),
                width=2,
                tags="selection"
            )

    def _is_inside_selection(self, x: int, y: int) -> bool:
        """Проверить, находится ли точка внутри выделения"""
        if self.start_x is None or self.start_y is None:
            return False

        x1, y1, x2, y2 = self._normalize_coords()
        return x1 <= x <= x2 and y1 <= y <= y2

    def _move_selection(self, new_x: int, new_y: int, model, canvas):
        """Переместить выделенную область"""
        if not model.selection or not self.selection_image:
            return

        x1, y1, x2, y2 = model.selection
        width = x2 - x1
        height = y2 - y1

        # Ограничиваем новые координаты границами изображения
        new_x = max(0, min(new_x, model.width - width))
        new_y = max(0, min(new_y, model.height - height))

        # Создаем временное изображение для предпросмотра
        temp_image = model.image.copy()

        # Очищаем старую область (делаем прозрачной)
        draw = ImageDraw.Draw(temp_image)
        draw.rectangle((x1, y1, x2, y2), fill=(0, 0, 0, 0))

        # Вставляем выделение в новое положение
        temp_image.paste(self.selection_image, (new_x, new_y), self.selection_image)

        # Временно показываем результат
        temp_tk_image = ImageTk.PhotoImage(temp_image)
        canvas.itemconfig(canvas.canvas_image_id, image=temp_tk_image)
        canvas.tk_image = temp_tk_image  # Сохраняем ссылку

        # Обновляем прямоугольник выделения
        if self.selection_rect:
            canvas.delete(self.selection_rect)

        self.selection_rect = canvas.create_rectangle(
            new_x, new_y, new_x + width, new_y + height,
            outline='blue',
            dash=(4, 2),
            width=2,
            tags="selection"
        )

    def clear_selection(self, canvas):
        """Очистить выделение"""
        if self.selection_rect:
            canvas.delete(self.selection_rect)
            self.selection_rect = None

        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.selection_image = None
        self.dragging = False
        self.moving = False