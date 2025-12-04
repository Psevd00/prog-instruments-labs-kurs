# gui/canvas.py
import tkinter as tk
from PIL import Image, ImageTk
from typing import Optional


class CanvasWidget(tk.Canvas):
    """Виджет холста с поддержкой инструментов"""

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.model = controller.model

        # Текущий инструмент
        self.current_tool = None

        # Переменные для отображения
        self.tk_image = None
        self.canvas_image_id = None

        # Привязка событий мыши
        self.bind("<ButtonPress-1>", self.on_mouse_down)
        self.bind("<B1-Motion>", self.on_mouse_move)
        self.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Привязка события прокрутки для масштабирования
        self.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.bind("<Button-4>", self.on_mouse_wheel)  # Linux
        self.bind("<Button-5>", self.on_mouse_wheel)  # Linux

        # Масштаб
        self.scale = 1.0

    def set_tool(self, tool):
        """Установить текущий инструмент"""
        if self.current_tool:
            self.current_tool.deactivate()

        self.current_tool = tool
        if tool:
            tool.activate()
            self.config(cursor=tool.cursor)

    def update_image(self):
        """Обновить изображение на холсте"""
        # Конвертируем PIL Image в PhotoImage для Tkinter
        self.tk_image = ImageTk.PhotoImage(self.model.image)

        # Создаем или обновляем изображение на холсте
        if self.canvas_image_id is not None:
            self.itemconfig(self.canvas_image_id, image=self.tk_image)
        else:
            self.canvas_image_id = self.create_image(
                0, 0,
                anchor=tk.NW,
                image=self.tk_image
            )

        # Если есть инструмент выделения, обновляем его прямоугольник
        if (self.current_tool and
                hasattr(self.current_tool, 'selection_rect') and
                self.current_tool.selection_rect):
            self.current_tool._update_selection_rect(self)

        # Обновляем область прокрутки
        self.update_scroll_region()

    def update_scroll_region(self):
        """Обновить область прокрутки"""
        self.config(scrollregion=(0, 0, self.model.width, self.model.height))

    def on_mouse_down(self, event):
        """Обработчик нажатия кнопки мыши"""
        if self.current_tool:
            # Преобразуем координаты с учетом масштаба и прокрутки
            x = self.canvasx(event.x)
            y = self.canvasy(event.y)

            # Создаем модифицированное событие с правильными координатами
            mod_event = type('Event', (), {
                'x': int(x),
                'y': int(y),
                'state': event.state
            })

            self.current_tool.on_mouse_down(mod_event, self.model, self)

    def on_mouse_move(self, event):
        """Обработчик перемещения мыши"""
        if self.current_tool:
            x = self.canvasx(event.x)
            y = self.canvasy(event.y)

            mod_event = type('Event', (), {
                'x': int(x),
                'y': int(y),
                'state': event.state
            })

            self.current_tool.on_mouse_move(mod_event, self.model, self)

            # Обновляем изображение на холсте
            self.update_image()

    def on_mouse_up(self, event):
        """Обработчик отпускания кнопки мыши"""
        if self.current_tool:
            x = self.canvasx(event.x)
            y = self.canvasy(event.y)

            mod_event = type('Event', (), {
                'x': int(x),
                'y': int(y),
                'state': event.state
            })

            self.current_tool.on_mouse_up(mod_event, self.model, self)

            # Обновляем изображение на холсте
            self.update_image()

    def on_mouse_wheel(self, event):
        """Обработчик прокрутки колеса мыши (масштабирование)"""
        if event.state & 0x4:  # Ctrl нажат
            scale_factor = 1.1

            if hasattr(event, 'delta'):  # Windows
                if event.delta > 0:
                    self.scale *= scale_factor
                else:
                    self.scale /= scale_factor
            else:  # Linux
                if event.num == 4:
                    self.scale *= scale_factor
                elif event.num == 5:
                    self.scale /= scale_factor

            # Ограничиваем масштаб
            self.scale = max(0.1, min(5.0, self.scale))

            # Обновляем изображение
            self.update_image()
            return "break"