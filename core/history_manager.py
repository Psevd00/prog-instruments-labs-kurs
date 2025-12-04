# core/history_manager.py
from typing import List, Any
import copy


class HistoryManager:
    """Управление историей действий для Undo/Redo"""

    def __init__(self, max_history: int = 50):
        self._undo_stack: List[Any] = []
        self._redo_stack: List[Any] = []
        self._max_history = max_history

    def push_state(self, state: Any):
        """Сохранить состояние в историю"""
        # Очищаем redo stack при новом действии
        self._redo_stack.clear()

        # Сохраняем глубокую копию состояния
        self._undo_stack.append(copy.deepcopy(state))

        # Ограничиваем размер истории
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)

    def undo(self, current_state: Any) -> Any:
        """Отменить последнее действие"""
        if not self._undo_stack:
            return current_state

        # Сохраняем текущее состояние в redo stack
        self._redo_stack.append(copy.deepcopy(current_state))

        # Восстанавливаем предыдущее состояние
        return self._undo_stack.pop()

    def redo(self, current_state: Any) -> Any:
        """Вернуть отмененное действие"""
        if not self._redo_stack:
            return current_state

        # Сохраняем текущее состояние в undo stack
        self._undo_stack.append(copy.deepcopy(current_state))

        # Восстанавливаем состояние из redo
        return self._redo_stack.pop()

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def clear(self):
        """Очистить историю"""
        self._undo_stack.clear()
        self._redo_stack.clear()