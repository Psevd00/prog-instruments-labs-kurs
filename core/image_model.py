2.	# core/image_model.py
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import numpy as np
from typing import Optional, Tuple, List
import copy


class ImageModel:
    """Модель, хранящая состояние изображения и данные"""

    def __init__(self, width: int = 800, height: int = 600, bg_color: Tuple = (255, 255, 255, 255)):
        self._image = Image.new("RGBA", (width, height), bg_color)
        self._original_image = self._image.copy()
        self._selection = None
        self._clipboard = None
        self._modified = False
        self._current_color = (0, 0, 0, 255)
        self._filepath = None

    @property
    def image(self) -> Image.Image:
        return self._image

    @property
    def width(self) -> int:
        return self._image.width

    @property
    def height(self) -> int:
        return self._image.height

    @property
    def selection(self) -> Optional[Tuple]:
        return self._selection

    @property
    def modified(self) -> bool:
        return self._modified

    @modified.setter
    def modified(self, value: bool):
        self._modified = value

    @property
    def current_color(self) -> Tuple:
        return self._current_color

    @current_color.setter
    def current_color(self, color: Tuple):
        self._current_color = color

    @property
    def filepath(self) -> Optional[str]:
        return self._filepath

    def create_new(self, width: int, height: int, bg_color: Tuple = (255, 255, 255, 255)):
        self._image = Image.new("RGBA", (width, height), bg_color)
        self._original_image = self._image.copy()
        self._selection = None
        self._modified = False
        self._filepath = None

    def load_image(self, filepath: str):
        try:
            self._image = Image.open(filepath).convert("RGBA")
            self._original_image = self._image.copy()
            self._modified = False
            self._filepath = filepath
        except Exception as e:
            raise ValueError(f"Ошибка загрузки: {e}")

    def save_image(self, filepath: str, format: str = "PNG"):
        try:
            if format.upper() == "JPEG" or format.upper() == "JPG":
                save_image = self._image.convert("RGB")
            else:
                save_image = self._image

            save_image.save(filepath, format=format)
            self._modified = False
            self._filepath = filepath
        except Exception as e:
            raise ValueError(f"Ошибка сохранения: {e}")

    def resize(self, new_width: int, new_height: int):
        if new_width <= 0 or new_height <= 0:
            raise ValueError("Размеры должны быть положительными")

        self._image = self._image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self._modified = True

    def rotate(self, angle: float):
        self._image = self._image.rotate(angle, expand=True)
        self._modified = True

    def crop(self, bbox: Tuple):
        self._image = self._image.crop(bbox)
        self._selection = None
        self._modified = True

    def apply_filter(self, filter_type: str, **kwargs):
        if filter_type == "grayscale":
            gray = self._image.convert("L")
            self._image = gray.convert("RGBA")

        elif filter_type == "invert":
            if self._image.mode == 'RGBA':
                r, g, b, a = self._image.split()
                rgb = Image.merge('RGB', (r, g, b))
                inverted = Image.eval(rgb, lambda x: 255 - x)
                r2, g2, b2 = inverted.split()
                self._image = Image.merge('RGBA', (r2, g2, b2, a))
            else:
                self._image = Image.eval(self._image, lambda x: 255 - x)

        elif filter_type == "brightness_contrast":
            brightness = kwargs.get('brightness', 0)
            contrast = kwargs.get('contrast', 0)

            brightness_factor = (brightness + 100) / 100.0
            contrast_factor = (contrast + 100) / 100.0

            enhancer = ImageEnhance.Brightness(self._image)
            img = enhancer.enhance(brightness_factor)

            enhancer = ImageEnhance.Contrast(img)
            self._image = enhancer.enhance(contrast_factor)

        self._modified = True

    def set_selection(self, bbox: Optional[Tuple]):
        self._selection = bbox

    def get_selection_image(self) -> Optional[Image.Image]:
        if self._selection:
            return self._image.crop(self._selection)
        return None

    def cut_selection(self):
        if self._selection:
            self._clipboard = self.get_selection_image()
            draw = ImageDraw.Draw(self._image)
            draw.rectangle(self._selection, fill=(0, 0, 0, 0))
            self._selection = None
            self._modified = True

    def copy_selection(self):
        if self._selection:
            self._clipboard = self.get_selection_image()

    def paste_from_clipboard(self, position: Tuple):
        if self._clipboard:
            self._image.paste(self._clipboard, position, self._clipboard)
            self._modified = True

    def delete_selection(self):
        if self._selection:
            draw = ImageDraw.Draw(self._image)
            draw.rectangle(self._selection, fill=(0, 0, 0, 0))
            self._selection = None
            self._modified = True

    def draw_pixel(self, x: int, y: int, color: Tuple, size: int = 1):
        if 0 <= x < self.width and 0 <= y < self.height:
            draw = ImageDraw.Draw(self._image)
            if size == 1:
                draw.point((x, y), fill=color)
            else:
                radius = size // 2
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
            self._modified = True

    def fill_area(self, x: int, y: int, color: Tuple):
        try:
            target_color = self._image.getpixel((x, y))
            if target_color == color:
                return

            img_array = np.array(self._image)
            h, w = img_array.shape[:2]
            stack = [(x, y)]
            visited = set()

            while stack:
                cx, cy = stack.pop()
                if (cx, cy) in visited:
                    continue
                if cx < 0 or cx >= w or cy < 0 or cy >= h:
                    continue
                if not np.array_equal(img_array[cy, cx], target_color):
                    continue

                img_array[cy, cx] = color
                visited.add((cx, cy))

                stack.append((cx + 1, cy))
                stack.append((cx - 1, cy))
                stack.append((cx, cy + 1))
                stack.append((cx, cy - 1))

            self._image = Image.fromarray(img_array, 'RGBA')
            self._modified = True
        except Exception as e:
            print(f"Ошибка заливки: {e}")

    def add_text(self, x: int, y: int, text: str, color: Tuple,
                 font_name: str = "Arial", font_size: int = 12):
        try:
            draw = ImageDraw.Draw(self._image)
            try:
                font = ImageFont.truetype(font_name, font_size)
            except:
                font = ImageFont.load_default()

            draw.text((x, y), text, fill=color, font=font)
            self._modified = True
        except Exception as e:
            print(f"Ошибка добавления текста: {e}")

    def get_pixel_color(self, x: int, y: int) -> Optional[Tuple]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._image.getpixel((x, y))
        return None
