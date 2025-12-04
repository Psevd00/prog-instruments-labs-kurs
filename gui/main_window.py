# gui/main_window.py
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk


class MainWindow:
    """Главное окно приложения (View)"""

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.model = controller.model

        # Создаем элементы интерфейса
        self._create_menu()
        self._create_canvas_area()

    def _create_menu(self):
        """Создать главное меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый...")
        file_menu.add_command(label="Открыть...")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе")

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

        # Холст Tkinter
        self.canvas = tk.Canvas(
            canvas_frame,
            bg="lightgray",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            scrollregion=(0, 0, self.model.width, self.model.height)
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)

        # Отображаем изображение на холсте
        self._display_image()

        # Привязываем событие изменения размера
        self.canvas.bind("<Configure>", self._update_scroll_region)

    def _display_image(self):
        """Отобразить изображение на холсте"""
        # Конвертируем PIL Image в PhotoImage для Tkinter
        self.tk_image = ImageTk.PhotoImage(self.model.image)

        # Создаем изображение на холсте
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Обновляем область прокрутки
        self._update_scroll_region()

    def _update_scroll_region(self, event=None):
        """Обновить область прокрутки"""
        self.canvas.config(scrollregion=(0, 0, self.model.width, self.model.height))