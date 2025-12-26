18.	# main.py
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
            self.root.title("Редактор растровой графики - v1.0")
            self.root.geometry("1200x800")

            # Инициализация модели
            self.model = ImageModel()
            self.history = HistoryManager(max_history=50)

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
        # Используем bind_all для глобальных горячих клавиш
        self.root.bind_all("<Control-z>", self._on_undo)
        self.root.bind_all("<Control-y>", self._on_redo)
        self.root.bind_all("<Control-Z>", self._on_undo)  # Shift+Z
        self.root.bind_all("<Control-Y>", self._on_redo)  # Shift+Y

        # Остальные горячие клавиши
        self.root.bind("<Control-s>", lambda e: self.view.save_image())
        self.root.bind("<Control-o>", lambda e: self.view.open_image())
        self.root.bind("<Control-n>", lambda e: self.view.create_new_image())
        self.root.bind("<Control-x>", lambda e: self.view.cut_selection())
        self.root.bind("<Control-c>", lambda e: self.view.copy_selection())
        self.root.bind("<Control-v>", lambda e: self.view.paste_selection())
        self.root.bind("<Delete>", lambda e: self.view.delete_selection())

    def _on_undo(self, event=None):
        """Обработчик Ctrl+Z"""
        self.undo()
        return "break"  # Предотвращаем дальнейшую обработку

    def _on_redo(self, event=None):
        """Обработчик Ctrl+Y"""
        self.redo()
        return "break"  # Предотвращаем дальнейшую обработку

    def save_state(self):
        """Сохранить текущее состояние в историю"""
        # Сохраняем копию текущего изображения
        if self.model.image:
            self.history.push_state(self.model.image.copy())

    def undo(self):
        """Отменить последнее действие"""
        if self.history.can_undo():
            # Получаем предыдущее состояние
            previous_state = self.history.undo(self.model.image.copy())

            # Восстанавливаем состояние
            self.model._image = previous_state
            self.model.modified = True
            self.model.set_selection(None)  # Очищаем выделение

            # Обновляем интерфейс
            self.view.update_image()
            self.view.status_label.config(text="Отменено последнее действие")

    def redo(self):
        """Вернуть отмененное действие"""
        if self.history.can_redo():
            # Получаем следующее состояние
            next_state = self.history.redo(self.model.image.copy())

            # Восстанавливаем состояние
            self.model._image = next_state
            self.model.modified = True
            self.model.set_selection(None)  # Очищаем выделение

            # Обновляем интерфейс
            self.view.update_image()
            self.view.status_label.config(text="Возвращено отмененное действие")

    def on_closing(self):
        """Обработчик закрытия окна"""
        if self.model.modified:
            response = messagebox.askyesnocancel(
                "Сохранение",
                "Изображение было изменено. Сохранить перед выходом?"
            )

            if response is None:
                return
            elif response:
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
