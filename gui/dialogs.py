4.	# gui/dialogs.py
import tkinter as tk
from tkinter import ttk, simpledialog, colorchooser
import tkinter.messagebox as messagebox


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

        input_frame = ttk.Frame(self.dialog, padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(input_frame, text="Ширина (пиксели):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.width_var = tk.StringVar(value="800")
        width_entry = ttk.Entry(input_frame, textvariable=self.width_var, width=15)
        width_entry.grid(row=0, column=1, pady=5, padx=(5, 0))

        ttk.Label(input_frame, text="Высота (пиксели):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.height_var = tk.StringVar(value="600")
        height_entry = ttk.Entry(input_frame, textvariable=self.height_var, width=15)
        height_entry.grid(row=1, column=1, pady=5, padx=(5, 0))

        ttk.Label(input_frame, text="Цвет фона:").grid(row=2, column=0, sticky=tk.W, pady=5)

        color_frame = ttk.Frame(input_frame)
        color_frame.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(5, 0))

        self.bg_color = (255, 255, 255, 255)
        self.color_preview = tk.Canvas(color_frame, width=20, height=20, bg="#FFFFFF",
                                       relief=tk.SUNKEN, bd=1)
        self.color_preview.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(color_frame, text="Выбрать...",
                   command=self._choose_color).pack(side=tk.LEFT)

        button_frame = ttk.Frame(self.dialog, padding="10")
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Создать",
                   command=self._on_create).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Отмена",
                   command=self._on_cancel).pack(side=tk.RIGHT)

        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.dialog.wait_window(self.dialog)

    def _choose_color(self):
        color_code = colorchooser.askcolor(title="Выберите цвет фона",
                                           initialcolor="#FFFFFF")
        if color_code[0]:
            rgb = tuple(map(int, color_code[0]))
            self.bg_color = rgb + (255,)
            self.color_preview.config(bg=color_code[1])

    def _on_create(self):
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
        self.dialog.destroy()


class ResizeDialog:
    """Диалог изменения размера изображения"""

    def __init__(self, parent, current_width, current_height):
        self.result = None
        self.current_width = current_width
        self.current_height = current_height
        self._create_dialog(parent)

    def _create_dialog(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Изменить размер")
        self.dialog.geometry("300x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        input_frame = ttk.Frame(self.dialog, padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(input_frame, text="Текущий размер:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(input_frame, text=f"{self.current_width} × {self.current_height}").grid(row=0, column=1, sticky=tk.W,
                                                                                          pady=5)

        ttk.Label(input_frame, text="Новая ширина:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.width_var = tk.StringVar(value=str(self.current_width))
        width_entry = ttk.Entry(input_frame, textvariable=self.width_var, width=15)
        width_entry.grid(row=1, column=1, pady=5, padx=(5, 0))

        ttk.Label(input_frame, text="Новая высота:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.height_var = tk.StringVar(value=str(self.current_height))
        height_entry = ttk.Entry(input_frame, textvariable=self.height_var, width=15)
        height_entry.grid(row=2, column=1, pady=5, padx=(5, 0))

        self.keep_aspect_var = tk.BooleanVar(value=True)
        keep_aspect_check = ttk.Checkbutton(input_frame, text="Сохранять пропорции",
                                            variable=self.keep_aspect_var)
        keep_aspect_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)

        button_frame = ttk.Frame(self.dialog, padding="10")
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Применить",
                   command=self._on_apply).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Отмена",
                   command=self._on_cancel).pack(side=tk.RIGHT)

        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.dialog.wait_window(self.dialog)

    def _on_apply(self):
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())

            if width <= 0 or height <= 0:
                raise ValueError("Размеры должны быть положительными")

            self.result = (width, height)
            self.dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")

    def _on_cancel(self):
        self.dialog.destroy()


class RotateDialog:
    """Диалог поворота изображения"""

    def __init__(self, parent):
        self.result = None
        self._create_dialog(parent)

    def _create_dialog(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Повернуть изображение")
        self.dialog.geometry("300x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        input_frame = ttk.Frame(self.dialog, padding="20")
        input_frame.pack(fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(input_frame)
        button_frame.pack(expand=True)

        angles = [("90° по часовой", 90), ("180°", 180),
                  ("90° против часовой", -90), ("Произвольный угол", "custom")]

        for i, (text, angle) in enumerate(angles):
            if angle == "custom":
                btn = ttk.Button(button_frame, text=text,
                                 command=self._custom_angle)
            else:
                btn = ttk.Button(button_frame, text=text,
                                 command=lambda a=angle: self._set_angle(a))
            btn.pack(pady=5, fill=tk.X)

        button_frame2 = ttk.Frame(self.dialog, padding="10")
        button_frame2.pack(fill=tk.X)

        ttk.Button(button_frame2, text="Отмена",
                   command=self._on_cancel).pack(side=tk.RIGHT, padx=5)

        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.dialog.wait_window(self.dialog)

    def _set_angle(self, angle):
        self.result = angle
        self.dialog.destroy()

    def _custom_angle(self):
        angle = simpledialog.askfloat("Поворот", "Введите угол поворота (градусы):",
                                      minvalue=-360, maxvalue=360)
        if angle is not None:
            self.result = angle
            self.dialog.destroy()

    def _on_cancel(self):
        self.dialog.destroy()


class BrightnessContrastDialog:
    """Диалог настройки яркости и контрастности"""

    def __init__(self, parent):
        self.result = None
        self._create_dialog(parent)

    def _create_dialog(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Яркость и контрастность")
        self.dialog.geometry("350x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        input_frame = ttk.Frame(self.dialog, padding="20")
        input_frame.pack(fill=tk.BOTH, expand=True)

        # Яркость
        ttk.Label(input_frame, text="Яркость:").pack(anchor=tk.W)
        self.brightness_var = tk.IntVar(value=0)
        brightness_scale = ttk.Scale(input_frame, from_=-100, to=100,
                                     variable=self.brightness_var,
                                     orient=tk.HORIZONTAL)
        brightness_scale.pack(fill=tk.X, pady=5)

        brightness_value = ttk.Label(input_frame, text="0")
        brightness_value.pack()

        # Контрастность
        ttk.Label(input_frame, text="Контрастность:").pack(anchor=tk.W, pady=(10, 0))
        self.contrast_var = tk.IntVar(value=0)
        contrast_scale = ttk.Scale(input_frame, from_=-100, to=100,
                                   variable=self.contrast_var,
                                   orient=tk.HORIZONTAL)
        contrast_scale.pack(fill=tk.X, pady=5)

        contrast_value = ttk.Label(input_frame, text="0")
        contrast_value.pack()

        # Привязка обновления значений
        def update_brightness(*args):
            brightness_value.config(text=str(self.brightness_var.get()))

        def update_contrast(*args):
            contrast_value.config(text=str(self.contrast_var.get()))

        self.brightness_var.trace("w", update_brightness)
        self.contrast_var.trace("w", update_contrast)

        button_frame = ttk.Frame(self.dialog, padding="10")
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Применить",
                   command=self._on_apply).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Отмена",
                   command=self._on_cancel).pack(side=tk.RIGHT)

        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.dialog.wait_window(self.dialog)

    def _on_apply(self):
        self.result = (self.brightness_var.get(), self.contrast_var.get())
        self.dialog.destroy()

    def _on_cancel(self):
        self.dialog.destroy()
