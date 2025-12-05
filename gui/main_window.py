# gui/main_window.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import ImageTk
import os
from gui.dialogs import NewImageDialog
from gui.canvas import CanvasWidget
from tools.brush_tool import BrushTool
from tools.eraser_tool import EraserTool
from tools.fill_tool import FillTool
from tools.pipette_tool import PipetteTool
from tools.selection_tool import SelectionTool
from utils.constants import DEFAULT_FG_COLOR


class MainWindow:
    """Главное окно приложения (View)"""

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.model = controller.model

        # Инструменты
        self.tools = {}
        self.current_tool = None

        # Текущий цвет
        self.current_color = DEFAULT_FG_COLOR

        # Создаем элементы интерфейса
        self._create_menu()
        self._create_toolbar()
        self._create_canvas_area()
        self._create_statusbar()
        self._create_color_palette()

        # Инициализация инструментов
        self._init_tools()

        # Активируем инструмент по умолчанию
        self.select_tool("brush")

    def _create_menu(self):
        """Создать главное меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый...", command=self.create_new_image,
                              accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть...", command=self.open_image,
                              accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_image,
                              accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как...", command=self.save_image_as)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Меню "Правка"
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Отменить", command=self.controller.undo,
                              accelerator="Ctrl+Z")
        edit_menu.add_command(label="Повторить", command=self.controller.redo,
                              accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=self.cut_selection,
                              accelerator="Ctrl+X")
        edit_menu.add_command(label="Копировать", command=self.copy_selection,
                              accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.paste_selection,
                              accelerator="Ctrl+V")
        edit_menu.add_command(label="Удалить", command=self.delete_selection,
                              accelerator="Del")

        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)

        # Привязка горячих клавиш
        self.root.bind("<Control-n>", lambda e: self.create_new_image())
        self.root.bind("<Control-o>", lambda e: self.open_image())
        self.root.bind("<Control-s>", lambda e: self.save_image())
        self.root.bind("<Control-x>", lambda e: self.cut_selection())
        self.root.bind("<Control-c>", lambda e: self.copy_selection())
        self.root.bind("<Control-v>", lambda e: self.paste_selection())
        self.root.bind("<Delete>", lambda e: self.delete_selection())

    def _create_toolbar(self):
        """Создать панель инструментов"""
        toolbar_frame = tk.Frame(self.root, relief=tk.RAISED, bd=2)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        # Кнопки инструментов
        tools = [
            ("Кисть", "🖌️", "brush"),
            ("Ластик", "🧽", "eraser"),
            ("Заливка", "🎨", "fill"),
            ("Выделение", "▢", "selection"),
            ("Пипетка", "🔍", "pipette"),
            ("Текст", "T", "text"),
        ]

        for text, icon, tool_id in tools:
            btn = tk.Button(toolbar_frame, text=f"{icon}",
                            command=lambda tid=tool_id: self.select_tool(tid),
                            relief=tk.RAISED,
                            width=3,
                            font=("Arial", 12))
            btn.pack(side=tk.LEFT, padx=2, pady=2)

            # Подсказка
            self._create_tooltip(btn, text)

        # Разделитель
        tk.Label(toolbar_frame, text="|").pack(side=tk.LEFT, padx=5)

        # Выбор размера кисти
        tk.Label(toolbar_frame, text="Размер:").pack(side=tk.LEFT, padx=5)
        self.brush_size_var = tk.IntVar(value=5)
        size_spin = tk.Spinbox(toolbar_frame, from_=1, to=50,
                               textvariable=self.brush_size_var,
                               width=5,
                               command=self._update_brush_size)
        size_spin.pack(side=tk.LEFT, padx=2)

        # Привязка события изменения
        self.brush_size_var.trace("w", lambda *args: self._update_brush_size())

    def _create_tooltip(self, widget, text):
        """Создать всплывающую подсказку"""

        def enter(event):
            self.status_label.config(text=text)

        def leave(event):
            self.update_status()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def _create_canvas_area(self):
        """Создать область холста"""
        # Фрейм для холста
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Полосы прокрутки
        v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Наш кастомный холст
        self.canvas = CanvasWidget(
            canvas_frame,
            self.controller,
            bg="lightgray",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)

        # Отображаем изображение
        self.canvas.update_image()

    def _create_statusbar(self):
        """Создать строку состояния"""
        self.statusbar = tk.Frame(self.root, relief=tk.SUNKEN, bd=1)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(self.statusbar, text="Готово")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Индикатор инструмента
        self.tool_label = tk.Label(self.statusbar, text="Инструмент: Кисть")
        self.tool_label.pack(side=tk.LEFT, padx=20)

        # Индикатор координат
        self.coords_label = tk.Label(self.statusbar, text="x: 0, y: 0")
        self.coords_label.pack(side=tk.RIGHT, padx=10)

        # Индикатор размера изображения
        self.image_size_label = tk.Label(self.statusbar,
                                         text=f"Размер: {self.model.width}x{self.model.height}")
        self.image_size_label.pack(side=tk.RIGHT, padx=10)

        # Привязка движения мыши к холсту для отображения координат
        self.canvas.bind("<Motion>", self._update_coords)

    def _create_color_palette(self):
        """Создать палитру цветов"""
        color_frame = tk.Frame(self.root, relief=tk.SUNKEN, bd=1)
        color_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Кнопка выбора цвета
        self.color_button = tk.Button(
            color_frame,
            text="Цвет",
            command=self.choose_color,
            bg="#000000",
            fg="#FFFFFF",
            width=8
        )
        self.color_button.pack(side=tk.LEFT, padx=5, pady=2)

        # Палитра часто используемых цветов
        colors = [
            "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF",
            "#FFFF00", "#FF00FF", "#00FFFF", "#808080", "#800000"
        ]

        for color in colors:
            btn = tk.Button(
                color_frame,
                bg=color,
                width=2,
                height=1,
                command=lambda c=color: self.set_color_from_hex(c)
            )
            btn.pack(side=tk.LEFT, padx=1, pady=2)

    def _init_tools(self):
        """Инициализировать инструменты"""
        # Кисть
        brush_tool = BrushTool()
        brush_tool.set_color(self.current_color)
        brush_tool.set_size(self.brush_size_var.get())
        self.tools["brush"] = brush_tool

        # Ластик
        eraser_tool = EraserTool()
        eraser_tool.set_size(self.brush_size_var.get())
        self.tools["eraser"] = eraser_tool

        # Заливка
        fill_tool = FillTool()
        fill_tool.set_color(self.current_color)
        self.tools["fill"] = fill_tool

        # Пипетка
        pipette_tool = PipetteTool()
        self.tools["pipette"] = pipette_tool

        # Выделение
        selection_tool = SelectionTool()
        self.tools["selection"] = selection_tool

        # TODO: инструмент Текст будет добавлен позже
        self.tools["text"] = None

    def select_tool(self, tool_id: str):
        """Выбрать инструмент"""
        if tool_id in self.tools and self.tools[tool_id] is not None:
            # Очищаем выделение при смене инструмента (кроме самого инструмента выделения)
            if tool_id != "selection" and self.tools["selection"]:
                self.tools["selection"].clear_selection(self.canvas)
                self.model.set_selection(None)

            self.current_tool = tool_id
            self.canvas.set_tool(self.tools[tool_id])
            self.tool_label.config(text=f"Инструмент: {self.tools[tool_id].name}")
        else:
            # Если инструмент еще не реализован
            self.status_label.config(text=f"Инструмент '{tool_id}' в разработке")

    def choose_color(self):
        """Выбрать цвет через диалог"""
        color_code = colorchooser.askcolor(
            title="Выберите цвет",
            initialcolor="#000000"
        )
        if color_code[0]:
            rgb = tuple(map(int, color_code[0]))
            self.set_color(rgb + (255,))  # Добавляем альфа-канал

    def set_color(self, color):
        """Установить текущий цвет"""
        self.current_color = color
        self.color_button.config(bg=f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}")

        # Обновляем цвет во всех инструментах, которые его поддерживают
        for tool_id, tool in self.tools.items():
            if tool and hasattr(tool, 'set_color'):
                tool.set_color(color)

    def set_color_from_hex(self, hex_color):
        """Установить цвет из HEX строки"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        self.set_color(rgb + (255,))

    def _update_brush_size(self):
        """Обновить размер кисти и ластика"""
        size = self.brush_size_var.get()

        if self.tools["brush"]:
            self.tools["brush"].set_size(size)

        if self.tools["eraser"]:
            self.tools["eraser"].set_size(size)

    def _update_coords(self, event):
        """Обновить координаты в строке состояния"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.coords_label.config(text=f"x: {int(x)}, y: {int(y)}")

    def cut_selection(self):
        """Вырезать выделенную область"""
        if self.model.selection:
            self.controller.save_state()  # Сохраняем состояние перед изменением
            self.model.cut_selection()
            self.update_image()
            # Очищаем выделение на холсте
            if self.tools["selection"]:
                self.tools["selection"].clear_selection(self.canvas)

    def copy_selection(self):
        """Копировать выделенную область"""
        if self.model.selection:
            self.model.copy_selection()
            self.status_label.config(text="Выделение скопировано в буфер")

    def paste_selection(self):
        """Вставить из буфера обмена"""
        self.controller.save_state()  # Сохраняем состояние перед изменением

        # Вставляем в центр видимой области холста
        canvas_x = self.canvas.winfo_width() // 2
        canvas_y = self.canvas.winfo_height() // 2

        # Преобразуем координаты холста в координаты изображения
        x = int(self.canvas.canvasx(canvas_x))
        y = int(self.canvas.canvasy(canvas_y))

        self.model.paste_from_clipboard((x, y))
        self.update_image()
        self.status_label.config(text="Вставлено из буфера")

    def delete_selection(self):
        """Удалить выделенную область"""
        if self.model.selection:
            self.controller.save_state()  # Сохраняем состояние перед изменением
            self.model.delete_selection()
            self.update_image()
            # Очищаем выделение на холсте
            if self.tools["selection"]:
                self.tools["selection"].clear_selection(self.canvas)

    def update_image(self):
        """Обновить изображение на холсте (делегируем холсту)"""
        self.canvas.update_image()
        self.update_status()

    def update_status(self):
        """Обновить строку состояния"""
        self.image_size_label.config(
            text=f"Размер: {self.model.width}x{self.model.height}"
        )

        filename = "Новое изображение"
        if self.model.filepath:
            filename = os.path.basename(self.model.filepath)

        status_text = filename
        if self.model.modified:
            status_text += " (изменено)"

        self.status_label.config(text=status_text)

    def create_new_image(self):
        """Создать новое изображение"""
        dialog = NewImageDialog(self.root)
        if dialog.result:
            width, height, bg_color = dialog.result
            self.model.create_new(width, height, bg_color)
            self.update_image()
            self.controller.save_state()

    def open_image(self):
        """Открыть изображение"""
        filetypes = [
            ("Все изображения", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("BMP files", "*.bmp"),
        ]

        filename = filedialog.askopenfilename(
            title="Открыть изображение",
            filetypes=filetypes
        )

        if filename:
            try:
                self.model.load_image(filename)
                self.update_image()
                self.status_label.config(text=f"Открыт файл: {os.path.basename(filename)}")
                self.controller.save_state()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")

    def save_image(self):
        """Сохранить изображение"""
        if self.model.filepath:
            try:
                # Определяем формат по расширению
                ext = os.path.splitext(self.model.filepath)[1].lower()
                format = "PNG" if ext == ".png" else "JPEG" if ext in [".jpg", ".jpeg"] else "PNG"

                self.model.save_image(self.model.filepath, format)
                self.update_status()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")
        else:
            self.save_image_as()

    def save_image_as(self):
        """Сохранить изображение как..."""
        filetypes = [
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("All files", "*.*"),
        ]

        filename = filedialog.asksaveasfilename(
            title="Сохранить изображение",
            defaultextension=".png",
            filetypes=filetypes
        )

        if filename:
            try:
                format = "PNG" if filename.lower().endswith('.png') else "JPEG"
                self.model.save_image(filename, format)
                self.update_status()
                self.status_label.config(text=f"Сохранено: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def show_about(self):
        """Показать информацию о программе"""
        messagebox.showinfo(
            "О программе",
            "Редактор растровой графики\n\n"
            "Версия 0.6\n"
            "Функционал: Открытие/сохранение, инструменты рисования, выделение\n\n"
            "Python, Tkinter, Pillow"
        )