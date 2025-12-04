# tools/fill_tool.py
from tools.base_tool import BaseTool
import numpy as np
from PIL import Image
from typing import Tuple


class FillTool(BaseTool):
    """Инструмент Заливка области"""

    def __init__(self):
        super().__init__(name="Заливка", icon="🎨")
        self.cursor = "spraycan"
        self.color = (0, 0, 0, 255)  # Чёрный по умолчанию

    def on_mouse_down(self, event, model, canvas):
        """Заливка области при клике"""
        x, y = event.x, event.y

        if 0 <= x < model.width and 0 <= y < model.height:
            try:
                self._flood_fill(model, x, y, self.color)
                model.modified = True
            except Exception as e:
                print(f"Ошибка заливки: {e}")

    def on_mouse_move(self, event, model, canvas):
        """Ничего не делаем при перемещении"""
        pass

    def on_mouse_up(self, event, model, canvas):
        """Ничего не делаем при отпускании"""
        pass

    def _flood_fill(self, model, x: int, y: int, fill_color: Tuple):
        """Алгоритм заливки области"""
        # Получаем целевой цвет (цвет пикселя, по которому кликнули)
        target_color = model.image.getpixel((x, y))

        # Если целевой цвет совпадает с цветом заливки, ничего не делаем
        if target_color == fill_color:
            return

        # Конвертируем изображение в массив numpy для быстрой обработки
        img_array = np.array(model.image)
        height, width = img_array.shape[:2]

        # Используем стек для flood fill
        stack = [(x, y)]
        visited = set()

        # Преобразуем цвета в tuple для сравнения
        target_color_np = np.array(target_color, dtype=np.uint8)
        fill_color_np = np.array(fill_color, dtype=np.uint8)

        while stack:
            cx, cy = stack.pop()

            # Проверяем границы
            if cx < 0 or cx >= width or cy < 0 or cy >= height:
                continue

            # Проверяем, не посещали ли уже эту точку
            if (cx, cy) in visited:
                continue

            # Проверяем, совпадает ли цвет с целевым
            if not np.array_equal(img_array[cy, cx], target_color_np):
                continue

            # Заливаем пиксель
            img_array[cy, cx] = fill_color_np
            visited.add((cx, cy))

            # Добавляем соседние пиксели
            stack.append((cx + 1, cy))
            stack.append((cx - 1, cy))
            stack.append((cx, cy + 1))
            stack.append((cx, cy - 1))

        # Обновляем изображение
        model._image = Image.fromarray(img_array, 'RGBA')

    def set_color(self, color: Tuple):
        """Установить цвет заливки"""
        self.color = color