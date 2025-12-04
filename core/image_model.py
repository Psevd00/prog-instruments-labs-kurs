# core/image_model.py
from PIL import Image
from typing import Optional, Tuple


class ImageModel:
    """Модель, хранящая состояние изображения"""

    def __init__(self, width: int = 800, height: int = 600, bg_color: Tuple = (255, 255, 255, 255)):
        self._image = Image.new("RGBA", (width, height), bg_color)
        self._modified = False

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