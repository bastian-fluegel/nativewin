"""Reactive state binding for nativewin widgets."""

from __future__ import annotations

from typing import Callable, List, Optional


class State:
    """Reactive string state with observer callbacks.

    Parameters
    ----------
    initial:
        Initial string value.
    """

    def __init__(self, initial: str = "") -> None:
        self._value = str(initial)
        self._observers: List[Callable[[str], None]] = []

    @property
    def value(self) -> str:
        """Current state value."""
        return self._value

    @value.setter
    def value(self, new_value: str) -> None:
        self.set(new_value)

    def set(self, new_value: str) -> None:
        """Update value and notify bound widgets."""
        text = str(new_value)
        if text == self._value:
            return
        self._value = text
        for callback in list(self._observers):
            callback(text)

    def bind(self, callback: Callable[[str], None]) -> None:
        """Register an observer invoked when value changes."""
        self._observers.append(callback)

    def unbind(self, callback: Callable[[str], None]) -> None:
        """Remove a previously registered observer."""
        try:
            self._observers.remove(callback)
        except ValueError:
            pass

    def __repr__(self) -> str:
        return f"State({self._value!r})"


class BoolState:
    """Reactive boolean state for checkbox binding."""

    def __init__(self, initial: bool = False) -> None:
        self._value = bool(initial)
        self._observers: List[Callable[[bool], None]] = []

    @property
    def value(self) -> bool:
        return self._value

    @value.setter
    def value(self, new_value: bool) -> None:
        self.set(new_value)

    def set(self, new_value: bool) -> None:
        checked = bool(new_value)
        if checked == self._value:
            return
        self._value = checked
        for callback in list(self._observers):
            callback(checked)

    def bind(self, callback: Callable[[bool], None]) -> None:
        self._observers.append(callback)

    def toggle(self) -> None:
        self.set(not self._value)
