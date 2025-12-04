# gui/dialogs.py
import tkinter as tk
from tkinter import ttk, simpledialog
from tkinter import colorchooser


class NewImageDialog:
    """Диалог создания нового изображения"""

    def __init__(self, parent):
        self.result = None
        self._create_dialog(parent)

    def _create_dialog(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Новое изображение")
        self.dialog.geometry("300x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Фрейм для полей ввода
        input_frame = ttk.Frame(self.dialog, padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True)

        # Ширина
        ttk.Label(input_frame, text="Ширина (пиксели):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.width_var = tk.StringVar(value="800")
        width_entry = ttk.Entry(input_frame, textvariable=self.width_var, width=15)
        width_entry.grid(row=0, column=1, pady=5, padx=(5, 0))

        # Высота
        ttk.Label(input_frame, text="Высота (пиксели):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.height_var = tk.StringVar(value="600")
        height_entry = ttk.Entry(input_frame, textvariable=self.height_var, width=15)
        height_entry.grid(row=1, column=1, pady=5, padx=(5, 0))

        # Цвет фона
        ttk.Label(input_frame, text="Цвет фона:").grid(row=2, column=0, sticky=tk.W, pady=5)

        color_frame = ttk.Frame(input_frame)
        color_frame.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        self.bg_color = (255, 255, 255, 255)  # Белый по умолчанию

        # Превью цвета
        self.color_preview = tk.Canvas(color_frame, width=20, height=20, bg="#FFFFFF",
                                       relief=tk.SUNKEN, bd=1)
        self.color_preview.pack(side=tk.LEFT, padx=(0, 5))

        # Кнопка выбора цвета
        ttk.Button(color_frame, text="Выбрать...",
                   command=self._choose_color).pack(side=tk.LEFT)

        # Кнопки
        button_frame = ttk.Frame(self.dialog, padding="10")
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Создать",
                   command=self._on_create).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Отмена",
                   command=self._on_cancel).pack(side=tk.RIGHT)

        # Центрируем диалог
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.dialog.wait_window(self.dialog)

    def _choose_color(self):
        """Выбрать цвет фона"""
        color_code = colorchooser.askcolor(title="Выберите цвет фона",
                                           initialcolor="#FFFFFF")
        if color_code[0]:
            rgb = tuple(map(int, color_code[0]))
            self.bg_color = rgb + (255,)  # Добавляем альфа-канал
            self.color_preview.config(bg=color_code[1])

    def _on_create(self):
        """Обработчик нажатия кнопки Создать"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())

            if width <= 0 or height <= 0:
                raise ValueError("Размеры должны быть положительными числами")

            self.result = (width, height, self.bg_color)
            self.dialog.destroy()
        except ValueError as e:
            tk.messagebox.showerror("Ошибка", f"Некорректные данные: {e}")

    def _on_cancel(self):
        """Обработчик нажатия кнопки Отмена"""
        self.dialog.destroy()