# core/image_model.py
from PIL import Image
from typing import Optional, Tuple


class ImageModel:
    """Модель, хранящая состояние изображения"""

    def __init__(self, width: int = 800, height: int = 600, bg_color: Tuple = (255, 255, 255, 255)):
        self._image = Image.new("RGBA", (width, height), bg_color)
        self._original_image = self._image.copy()
        self._modified = False
        self._filepath = None  # Текущий путь к файлу
        self._selection = None
        self._clipboard = None  # Добавляем буфер обмена

    @property
    def image(self) -> Image.Image:
        """Возвращает текущее изображение"""
        return self._image

    @property
    def width(self) -> int:
        return self._image.width

    @property
    def height(self) -> int:
        return self._image.height

    @property
    def modified(self) -> bool:
        return self._modified

    @modified.setter
    def modified(self, value: bool):
        self._modified = value

    @property
    def filepath(self) -> Optional[str]:
        return self._filepath

    def create_new(self, width: int, height: int, bg_color: Tuple = (255, 255, 255, 255)):
        """Создать новое изображение"""
        self._image = Image.new("RGBA", (width, height), bg_color)
        self._original_image = self._image.copy()
        self._modified = False
        self._filepath = None

    def load_image(self, filepath: str):
        """Загрузить изображение из файла"""
        try:
            self._image = Image.open(filepath).convert("RGBA")
            self._original_image = self._image.copy()
            self._modified = False
            self._filepath = filepath
        except Exception as e:
            raise ValueError(f"Ошибка загрузки изображения: {e}")

    def save_image(self, filepath: str, format: str = "PNG"):
        """Сохранить изображение в файл"""
        try:
            # Конвертируем в RGB для JPEG
            if format.upper() == "JPEG" or format.upper() == "JPG":
                save_image = self._image.convert("RGB")
            else:
                save_image = self._image

            save_image.save(filepath, format=format)
            self._modified = False
            self._filepath = filepath
        except Exception as e:
            raise ValueError(f"Ошибка сохранения: {e}")

    def set_selection(self, bbox: Optional[Tuple]):
        """Установить область выделения"""
        self._selection = bbox

    @property
    def selection(self) -> Optional[Tuple]:
        return self._selection

    def get_selection_image(self) -> Optional[Image.Image]:
        """Получить изображение выделенной области"""
        if self._selection:
            return self._image.crop(self._selection)
        return None

    def cut_selection(self):
        """Вырезать выделенную область"""
        if self._selection:
            self._clipboard = self.get_selection_image()
            # Заполняем область прозрачным цветом
            from PIL import ImageDraw
            draw = ImageDraw.Draw(self._image)
            draw.rectangle(self._selection, fill=(0, 0, 0, 0))
            self._selection = None
            self._modified = True

    def copy_selection(self):
        """Копировать выделенную область"""
        if self._selection:
            self._clipboard = self.get_selection_image()

    def paste_from_clipboard(self, position: Tuple):
        """Вставить из буфера обмена"""
        if self._clipboard:
            self._image.paste(self._clipboard, position, self._clipboard)
            self._modified = True

    def delete_selection(self):
        """Удалить выделенную область"""
        if self._selection:
            from PIL import ImageDraw
            draw = ImageDraw.Draw(self._image)
            draw.rectangle(self._selection, fill=(0, 0, 0, 0))
            self._selection = None
            self._modified = True