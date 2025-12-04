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