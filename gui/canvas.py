# gui/canvas.py
import tkinter as tk
from PIL import Image, ImageTk
from typing import Optional
from tools.selection_tool import SelectionTool


class CanvasWidget(tk.Canvas):
    """Виджет холста с поддержкой инструментов"""

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.model = controller.model
        self.current_tool = None
        self.tk_image = None
        self.canvas_image_id = None
        self.scale = 1.0

        self.bind("<ButtonPress-1>", self.on_mouse_down)
        self.bind("<B1-Motion>", self.on_mouse_move)
        self.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.bind("<MouseWheel>", self.on_mouse_wheel)
        self.bind("<Button-4>", self.on_mouse_wheel)
        self.bind("<Button-5>", self.on_mouse_wheel)

    def set_tool(self, tool):
        if self.current_tool:
            self.current_tool.deactivate()

        self.current_tool = tool
        if tool:
            tool.activate()
            self.config(cursor=tool.cursor)

    def update_image(self):
        """Обновить изображение на холсте"""
        if self.model.image:
            self.tk_image = ImageTk.PhotoImage(self.model.image)

            if self.canvas_image_id is not None:
                self.itemconfig(self.canvas_image_id, image=self.tk_image)
            else:
                self.canvas_image_id = self.create_image(
                    0, 0,
                    anchor=tk.NW,
                    image=self.tk_image,
                    tags="image"
                )

            # Очищаем старые элементы выделения
            self.delete("selection")
            self.delete("selection_handle")

            # Восстанавливаем выделение после обновления изображения
            if (self.current_tool and
                    isinstance(self.current_tool, SelectionTool) and
                    self.model.selection):

                x1, y1, x2, y2 = self.model.selection

                # Создаем прямоугольник выделения
                self.current_tool.selection_rect = self.create_rectangle(
                    x1, y1, x2, y2,
                    outline='blue',
                    dash=(4, 2),
                    width=2,
                    tags="selection"
                )

                # Создаем ручки для изменения размера
                handle_size = 6
                handles_positions = [
                    (x1, y1),  # верхний левый
                    (x2, y1),  # верхний правый
                    (x1, y2),  # нижний левый
                    (x2, y2),  # нижний правый
                ]

                self.current_tool.selection_handles = []
                for hx, hy in handles_positions:
                    handle = self.create_rectangle(
                        hx - handle_size, hy - handle_size,
                        hx + handle_size, hy + handle_size,
                        fill='white',
                        outline='blue',
                        width=1,
                        tags="selection_handle"
                    )
                    self.current_tool.selection_handles.append(handle)

                # Обновляем флаги в инструменте
                self.current_tool.has_selection = True
                self.current_tool.start_x = x1
                self.current_tool.start_y = y1
                self.current_tool.current_x = x2
                self.current_tool.current_y = y2

            # Устанавливаем правильный порядок элементов:
            # 1. Изображение должно быть на самом нижнем слое
            self.tag_lower("image")
            # 2. Прямоугольник выделения и ручки - поверх изображения
            self.tag_raise("selection")
            self.tag_raise("selection_handle")

            self.update_scroll_region()

    def update_scroll_region(self):
        """Обновить область прокрутки"""
        if self.model.image:
            self.config(scrollregion=(0, 0, self.model.width, self.model.height))

    def on_mouse_down(self, event):
        if self.current_tool:
            x = self.canvasx(event.x)
            y = self.canvasy(event.y)

            # Создаем объект события с правильными координатами
            class ModifiedEvent:
                def __init__(self, x, y, state):
                    self.x = int(x)
                    self.y = int(y)
                    self.state = state

            mod_event = ModifiedEvent(x, y, event.state)
            self.current_tool.on_mouse_down(mod_event, self.model, self)

    def on_mouse_move(self, event):
        if self.current_tool:
            x = self.canvasx(event.x)
            y = self.canvasy(event.y)

            class ModifiedEvent:
                def __init__(self, x, y, state):
                    self.x = int(x)
                    self.y = int(y)
                    self.state = state

            mod_event = ModifiedEvent(x, y, event.state)
            self.current_tool.on_mouse_move(mod_event, self.model, self)

    def on_mouse_up(self, event):
        if self.current_tool:
            x = self.canvasx(event.x)
            y = self.canvasy(event.y)

            class ModifiedEvent:
                def __init__(self, x, y, state):
                    self.x = int(x)
                    self.y = int(y)
                    self.state = state

            mod_event = ModifiedEvent(x, y, event.state)
            self.current_tool.on_mouse_up(mod_event, self.model, self)
            self.update_image()

    def on_mouse_wheel(self, event):
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