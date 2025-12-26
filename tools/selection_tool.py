14.	# tools/selection_tool.py
from tools.base_tool import BaseTool
from PIL import Image, ImageDraw, ImageTk
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
        self.current_x = None
        self.current_y = None
        self.dragging = False
        self.moving = False
        self.has_selection = False

        # Визуальное представление
        self.selection_rect = None
        self.selection_handles = []  # Ручки для изменения размера
        self.selection_image = None
        self.original_image_backup = None

        # Для перемещения
        self.move_start_x = None
        self.move_start_y = None
        self.original_selection_pos = None

    def on_mouse_down(self, event, model, canvas):
        # Сохраняем состояние перед операцией с выделением
        if hasattr(canvas, 'controller'):
            canvas.controller.save_state()

        x, y = event.x, event.y

        if self.has_selection and self._is_inside_selection(x, y):
            # Начало перемещения существующего выделения
            self.moving = True
            self.move_start_x = x
            self.move_start_y = y
            self.original_selection_pos = model.selection

            # Сохраняем копию оригинального изображения для предпросмотра
            self.original_image_backup = model.image.copy()
            self.selection_image = model.get_selection_image()

        else:
            # Начало нового выделения
            self.dragging = True
            self.start_x = x
            self.start_y = y
            self.current_x = x
            self.current_y = y
            self.has_selection = False
            model.set_selection(None)

            # Очищаем старое выделение
            self._clear_selection_display(canvas)

            # Создаем новое выделение
            self._update_selection_rect(canvas)

    def on_mouse_move(self, event, model, canvas):
        x, y = event.x, event.y

        if self.moving and model.selection and self.selection_image:
            # Перемещение выделения с предпросмотром
            self._move_selection_preview(x, y, model, canvas)

        elif self.dragging:
            # Изменение размера выделения
            self.current_x = x
            self.current_y = y
            self._update_selection_rect(canvas)

    def on_mouse_up(self, event, model, canvas):
        x, y = event.x, event.y

        if self.dragging:
            # Завершение выделения
            self.dragging = False
            self.current_x = x
            self.current_y = y

            # Нормализуем координаты
            x1, y1, x2, y2 = self._normalize_coords()

            # Проверяем, что выделение не нулевое
            if abs(x2 - x1) > 2 and abs(y2 - y1) > 2:
                self.has_selection = True
                model.set_selection((x1, y1, x2, y2))
                self.selection_image = model.get_selection_image()

                # Добавляем ручки для изменения размера
                self._add_resize_handles(canvas, x1, y1, x2, y2)
            else:
                self.has_selection = False
                model.set_selection(None)
                self.selection_image = None
                self._clear_selection_display(canvas)

        elif self.moving:
            # Завершение перемещения
            self.moving = False

            if model.selection and self.selection_image:
                # Применяем перемещение
                x1, y1, x2, y2 = self.original_selection_pos
                width = x2 - x1
                height = y2 - y1

                # Рассчитываем смещение
                dx = x - self.move_start_x
                dy = y - self.move_start_y

                new_x1 = max(0, min(x1 + dx, model.width - width))
                new_y1 = max(0, min(y1 + dy, model.height - height))
                new_x2 = new_x1 + width
                new_y2 = new_y1 + height

                # Обновляем изображение
                if self.original_image_backup:
                    model._image = self.original_image_backup.copy()

                # Очищаем старую область
                draw = ImageDraw.Draw(model.image)
                draw.rectangle((x1, y1, x2, y2), fill=(0, 0, 0, 0))

                # Вставляем в новое положение
                model.image.paste(self.selection_image, (new_x1, new_y1), self.selection_image)

                # Обновляем выделение
                model.set_selection((new_x1, new_y1, new_x2, new_y2))
                model.modified = True

                # Обновляем отображение
                self._update_selection_rect(canvas)
                self._add_resize_handles(canvas, new_x1, new_y1, new_x2, new_y2)

            self.original_image_backup = None

        canvas.update_image()

    def _normalize_coords(self) -> Tuple:
        """Нормализовать координаты прямоугольника"""
        if self.start_x is None or self.start_y is None:
            return (0, 0, 0, 0)

        x1 = min(self.start_x, self.current_x)
        y1 = min(self.start_y, self.current_y)
        x2 = max(self.start_x, self.current_x)
        y2 = max(self.start_y, self.current_y)

        return (x1, y1, x2, y2)

    def _update_selection_rect(self, canvas):
        """Обновить визуальное отображение выделения"""
        # Удаляем старое выделение
        self._clear_selection_display(canvas)

        # Создаем новое выделение
        if self.start_x is not None and self.current_x is not None:
            x1, y1, x2, y2 = self._normalize_coords()

            # Рисуем пунктирный прямоугольник
            self.selection_rect = canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='blue',
                dash=(4, 2),
                width=2,
                tags="selection"
            )

    def _add_resize_handles(self, canvas, x1, y1, x2, y2):
        """Добавить ручки для изменения размера выделения"""
        handle_size = 6

        # Угловые ручки
        handles_positions = [
            (x1, y1),  # верхний левый
            (x2, y1),  # верхний правый
            (x1, y2),  # нижний левый
            (x2, y2),  # нижний правый
        ]

        for hx, hy in handles_positions:
            handle = canvas.create_rectangle(
                hx - handle_size, hy - handle_size,
                hx + handle_size, hy + handle_size,
                fill='white',
                outline='blue',
                width=1,
                tags="selection_handle"
            )
            self.selection_handles.append(handle)

    def _clear_selection_display(self, canvas):
        """Очистить визуальное отображение выделения"""
        if self.selection_rect:
            canvas.delete(self.selection_rect)
            self.selection_rect = None

        for handle in self.selection_handles:
            canvas.delete(handle)
        self.selection_handles.clear()

    def _is_inside_selection(self, x: int, y: int) -> bool:
        """Проверить, находится ли точка внутри выделения"""
        if not self.has_selection or self.start_x is None or self.start_y is None:
            return False

        x1, y1, x2, y2 = self._normalize_coords()
        return x1 <= x <= x2 and y1 <= y <= y2

    def _move_selection_preview(self, x: int, y: int, model, canvas):
        """Предпросмотр перемещения выделения"""
        if not self.original_selection_pos or not self.selection_image:
            return

        x1, y1, x2, y2 = self.original_selection_pos
        width = x2 - x1
        height = y2 - y1

        # Рассчитываем смещение
        dx = x - self.move_start_x
        dy = y - self.move_start_y

        # Новые координаты с ограничениями
        new_x1 = max(0, min(x1 + dx, model.width - width))
        new_y1 = max(0, min(y1 + dy, model.height - height))

        # Восстанавливаем оригинальное изображение
        if self.original_image_backup:
            temp_image = self.original_image_backup.copy()
        else:
            temp_image = model.image.copy()

        # Очищаем старую область в preview
        draw = ImageDraw.Draw(temp_image)
        draw.rectangle((x1, y1, x2, y2), fill=(0, 0, 0, 0))

        # Вставляем выделение в новое положение
        temp_image.paste(self.selection_image, (new_x1, new_y1), self.selection_image)

        # Показываем preview
        temp_tk_image = ImageTk.PhotoImage(temp_image)
        canvas.itemconfig(canvas.canvas_image_id, image=temp_tk_image)
        canvas.tk_image = temp_tk_image

        # Обновляем прямоугольник выделения
        self._clear_selection_display(canvas)
        self.selection_rect = canvas.create_rectangle(
            new_x1, new_y1, new_x1 + width, new_y1 + height,
            outline='blue',
            dash=(4, 2),
            width=2,
            tags="selection"
        )
        self._add_resize_handles(canvas, new_x1, new_y1,
                                 new_x1 + width, new_y1 + height)

    def clear_selection(self, canvas):
        """Очистить выделение"""
        self._clear_selection_display(canvas)
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.has_selection = False
        self.dragging = False
        self.moving = False
        self.selection_image = None
        self.original_image_backup = None

    def select_tool(self, tool_id: str):
        """Выбрать инструмент"""
        if tool_id in self.tools and self.tools[tool_id] is not None:
            # Очищаем выделение при смене инструмента (кроме самого инструмента выделения)
            if tool_id != "selection" and self.tools["selection"]:
                self.tools["selection"].clear_selection(self.canvas)
                self.model.set_selection(None)

            # Очищаем все предпросмотры при смене инструмента
            self.canvas.delete("preview")

            self.current_tool = tool_id
            self.canvas.set_tool(self.tools[tool_id])
            self.tool_label.config(text=f"Инструмент: {self.tools[tool_id].name}")
        else:
            self.status_label.config(text=f"Инструмент '{tool_id}' в разработке")

    def _update_fill_mode(self):
        """Обновить режим заливки для инструментов"""
        fill = self.fill_var.get()
        for tool_id in ["rectangle", "ellipse"]:
            if tool_id in self.tools and self.tools[tool_id]:
                self.tools[tool_id].set_fill(fill)
