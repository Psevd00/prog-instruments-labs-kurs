16.	# tools/text_tool.py
from tools.base_tool import BaseTool
import tkinter as tk
from tkinter import simpledialog, font
from PIL import ImageFont, ImageDraw
import os
import sys
from typing import Tuple


class TextTool(BaseTool):
    """Инструмент для добавления текста"""

    def __init__(self):
        super().__init__(name="Текст", icon="T")
        self.cursor = "xterm"
        self.color = (0, 0, 0, 255)
        self.font_size = 12

        # Получаем системный шрифт с поддержкой кириллицы
        self.font_name = self._get_system_font()
        print(f"Используемый шрифт: {self.font_name}")

    def _get_system_font(self):
        """Получить системный шрифт с поддержкой кириллицы"""
        # Определяем операционную систему
        if sys.platform == "win32":
            # Windows
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/times.ttf",
                "C:/Windows/Fonts/verdana.ttf",
                "C:/Windows/Fonts/tahoma.ttf",
                "C:/Windows/Fonts/calibri.ttf",
            ]
        elif sys.platform == "darwin":
            # macOS
            font_paths = [
                "/System/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Times.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Geneva.ttf",
            ]
        else:
            # Linux
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/msttcorefonts/arial.ttf",
            ]

        # Пробуем найти существующий шрифт
        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path

        # Если не нашли файл шрифта, пробуем получить через Tkinter
        try:
            # Получаем список доступных шрифтов
            available_fonts = list(font.families())

            # Приоритетные шрифты с поддержкой кириллицы
            cyrillic_fonts = [
                "Arial", "Times New Roman", "Verdana", "Tahoma",
                "Calibri", "Courier New", "DejaVu Sans",
                "Liberation Sans", "Ubuntu", "Roboto"
            ]

            for font_name in cyrillic_fonts:
                if font_name in available_fonts:
                    return font_name

            # Если не нашли, берем первый доступный
            if available_fonts:
                return available_fonts[0]

        except:
            pass

        # Последнее средство - стандартный шрифт
        return None

    def on_mouse_down(self, event, model, canvas):
        # Сохраняем состояние перед добавлением текста
        if hasattr(canvas, 'controller'):
            canvas.controller.save_state()

        x, y = event.x, event.y

        # Создаем диалоговое окно для ввода текста
        dialog = tk.Toplevel(canvas)
        dialog.title("Введите текст")
        dialog.geometry("400x200")
        dialog.transient(canvas)
        dialog.grab_set()

        # Текстовое поле
        text_frame = tk.Frame(dialog, padx=10, pady=10)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_label = tk.Label(text_frame, text="Текст:")
        text_label.pack(anchor=tk.W)

        text_entry = tk.Text(text_frame, height=5, width=40)
        text_entry.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        text_entry.focus_set()

        # Добавляем поле для размера шрифта
        font_frame = tk.Frame(text_frame)
        font_frame.pack(fill=tk.X, pady=5)

        tk.Label(font_frame, text="Размер шрифта:").pack(side=tk.LEFT)

        font_size_var = tk.IntVar(value=self.font_size)
        font_size_spin = tk.Spinbox(font_frame, from_=8, to=72,
                                    textvariable=font_size_var, width=5)
        font_size_spin.pack(side=tk.LEFT, padx=5)

        # Кнопки
        button_frame = tk.Frame(dialog, padx=10, pady=10)
        button_frame.pack(fill=tk.X)

        def add_text():
            text = text_entry.get("1.0", tk.END).strip()
            if text:
                try:
                    # Получаем размер шрифта
                    font_size = font_size_var.get()

                    # Пробуем загрузить шрифт
                    font_obj = None
                    if self.font_name and os.path.exists(self.font_name):
                        # Если это путь к файлу
                        try:
                            font_obj = ImageFont.truetype(self.font_name, font_size)
                        except:
                            pass
                    elif self.font_name:
                        # Если это имя шрифта
                        try:
                            font_obj = ImageFont.truetype(self.font_name, font_size)
                        except:
                            # Пробуем найти файл по имени
                            font_obj = self._find_font_by_name(self.font_name, font_size)

                    # Если не удалось загрузить шрифт, используем стандартный
                    if not font_obj:
                        print("Используется стандартный шрифт")
                        font_obj = ImageFont.load_default()
                    else:
                        print(f"Шрифт загружен: {self.font_name}, размер: {font_size}")

                    # Добавляем текст на изображение
                    draw = ImageDraw.Draw(model.image)
                    draw.text((x, y), text, fill=self.color, font=font_obj)
                    model.modified = True
                    canvas.update_image()

                except Exception as e:
                    print(f"Ошибка добавления текста: {e}")
                    import traceback
                    traceback.print_exc()

            dialog.destroy()

        tk.Button(button_frame, text="Добавить",
                  command=add_text).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Отмена",
                  command=dialog.destroy).pack(side=tk.RIGHT)

        # Центрируем диалог
        dialog.update_idletasks()
        dialog_x = canvas.winfo_rootx() + (canvas.winfo_width() // 2) - (dialog.winfo_width() // 2)
        dialog_y = canvas.winfo_rooty() + (canvas.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{dialog_x}+{dialog_y}")

        # Привязываем Enter для быстрого добавления
        text_entry.bind("<Return>", lambda e: add_text())

    def _find_font_by_name(self, font_name, font_size):
        """Найти файл шрифта по имени"""
        # Общие пути к шрифтам для разных ОС
        common_paths = []

        if sys.platform == "win32":
            common_paths = ["C:/Windows/Fonts/"]
        elif sys.platform == "darwin":
            common_paths = [
                "/System/Library/Fonts/",
                "/Library/Fonts/",
                "~/Library/Fonts/"
            ]
        else:
            common_paths = [
                "/usr/share/fonts/",
                "/usr/local/share/fonts/",
                "~/.fonts/"
            ]

        # Расширения файлов шрифтов
        extensions = ['.ttf', '.otf', '.ttc']

        # Ищем файл шрифта
        for path in common_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                for root, dirs, files in os.walk(expanded_path):
                    for file in files:
                        if any(file.lower().startswith(font_name.lower().replace(" ", ""))
                               for font_name_part in font_name.split()):
                            if any(file.lower().endswith(ext) for ext in extensions):
                                font_path = os.path.join(root, file)
                                try:
                                    return ImageFont.truetype(font_path, font_size)
                                except:
                                    continue

        return None

    def on_mouse_move(self, event, model, canvas):
        pass

    def on_mouse_up(self, event, model, canvas):
        pass

    def set_color(self, color: Tuple):
        self.color = color

    def set_font_size(self, size: int):
        if size > 0:
            self.font_size = size
