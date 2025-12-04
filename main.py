# main.py
import tkinter as tk
from core.image_model import ImageModel
from gui.main_window import MainWindow


class ImageEditorApp:
    """Главный класс приложения (Controller)"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Редактор растровой графики - v0.1")
        self.root.geometry("1024x768")

        # Инициализация модели
        self.model = ImageModel()

        # Инициализация представления
        self.view = MainWindow(self.root, self)

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