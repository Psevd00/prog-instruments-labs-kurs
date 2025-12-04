# main.py
import tkinter as tk
from tkinter import messagebox
from core.image_model import ImageModel
from core.history_manager import HistoryManager
from gui.main_window import MainWindow


class ImageEditorApp:
    """Главный класс приложения (Controller)"""

    def __init__(self):
        try:
            self.root = tk.Tk()
            self.root.title("Редактор растровой графики - v0.4")
            self.root.geometry("1200x800")

            # Инициализация модели
            self.model = ImageModel()
            self.history = HistoryManager()

            # Инициализация представления
            self.view = MainWindow(self.root, self)

            # Привязка горячих клавиш
            self._bind_shortcuts()

            # Обработка закрытия окна
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

            # Сохраняем начальное состояние
            self.save_state()

        except Exception as e:
            messagebox.showerror("Ошибка запуска", f"Не удалось запустить приложение:\n{e}")
            raise

    def _bind_shortcuts(self):
        """Привязать горячие клавиши"""
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-s>", lambda e: self.view.save_image())
        self.root.bind("<Control-o>", lambda e: self.view.open_image())
        self.root.bind("<Control-n>", lambda e: self.view.create_new_image())

    def save_state(self):
        """Сохранить текущее состояние в историю"""
        self.history.push_state(self.model.image.copy())

    def undo(self):
        """Отменить последнее действие"""
        if self.history.can_undo():
            image_state = self.history.undo(self.model.image)
            self.model._image = image_state
            self.model.modified = True
            self.view.update_image()

    def redo(self):
        """Вернуть отмененное действие"""
        if self.history.can_redo():
            image_state = self.history.redo(self.model.image)
            self.model._image = image_state
            self.model.modified = True
            self.view.update_image()

    def on_closing(self):
        """Обработчик закрытия окна"""
        if self.model.modified:
            response = messagebox.askyesnocancel(
                "Сохранение",
                "Изображение было изменено. Сохранить перед выходом?"
            )

            if response is None:  # Нажата Отмена
                return
            elif response:  # Нажата Да
                self.view.save_image()

        self.root.destroy()

    def run(self):
        """Запустить приложение"""
        self.root.mainloop()


def main():
    app = ImageEditorApp()
    app.run()


if __name__ == "__main__":
    main()