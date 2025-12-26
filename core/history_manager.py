1.	# core/history_manager.py
from typing import List, Any
import copy
from PIL import Image


class HistoryManager:
    """Управление историей действий для Undo/Redo"""

    def __init__(self, max_history: int = 50):
        self._undo_stack: List[Image.Image] = []
        self._redo_stack: List[Image.Image] = []
        self._max_history = max_history

    def push_state(self, state: Image.Image):
        """Сохранить состояние в историю"""
        # Очищаем redo stack при новом действии
        self._redo_stack.clear()

        # Сохраняем копию состояния
        state_copy = state.copy()

        # Проверяем, не идентично ли новое состояние последнему в истории
        if self._undo_stack:
            last_state = self._undo_stack[-1]
            if self._images_equal(state_copy, last_state):
                return  # Не сохраняем одинаковые состояния

        self._undo_stack.append(state_copy)

        # Ограничиваем размер истории
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)

    def _images_equal(self, img1: Image.Image, img2: Image.Image) -> bool:
        """Проверить, идентичны ли два изображения"""
        if img1.size != img2.size or img1.mode != img2.mode:
            return False

        # Сравниваем данные пикселей
        return list(img1.getdata()) == list(img2.getdata())

    def undo(self, current_state: Image.Image) -> Image.Image:
        """Отменить последнее действие"""
        if not self._undo_stack:
            return current_state

        # Сохраняем текущее состояние в redo stack
        self._redo_stack.append(current_state.copy())

        # Восстанавливаем предыдущее состояние
        previous_state = self._undo_stack.pop()

        return previous_state

    def redo(self, current_state: Image.Image) -> Image.Image:
        """Вернуть отмененное действие"""
        if not self._redo_stack:
            return current_state

        # Сохраняем текущее состояние в undo stack
        self._undo_stack.append(current_state.copy())

        # Восстанавливаем состояние из redo
        next_state = self._redo_stack.pop()

        return next_state

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 1  # >1 потому что текущее состояние тоже в стеке

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def clear(self):
        """Очистить историю"""
        self._undo_stack.clear()
        self._redo_stack.clear()
