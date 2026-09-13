"""Declarative layout managers: vstack, hstack, groupbox slot positioning."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Generator, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from nativewin.window.form import Window
    from nativewin.widgets.base import Widget


@dataclass
class LayoutSlot:
    """Geometry slot assigned to a widget within a container."""

    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0


@dataclass
class LayoutContainer:
    """Stack or group container collecting child widgets."""

    kind: str
    padding: int = 8
    spacing: int = 6
    title: str = ""
    fixed_height: Optional[int] = None
    children: List["Widget"] = field(default_factory=list)
    parent: Optional["LayoutContainer"] = None

    def add(self, widget: "Widget") -> "Widget":
        """Register a widget in this container."""
        self.children.append(widget)
        widget._container = self  # noqa: SLF001
        return widget


_layout_stack: List[LayoutContainer] = []
_current_window: Optional["Window"] = None


def _current_container() -> LayoutContainer:
    if not _layout_stack:
        raise RuntimeError("Layout context required: use 'with nw.vstack():'")
    return _layout_stack[-1]


def set_active_window(window: "Window") -> None:
    """Set the window receiving subsequent layout widgets."""
    global _current_window
    _current_window = window


def get_active_window() -> "Window":
    if _current_window is None:
        raise RuntimeError("No active Window for layout")
    return _current_window


def push_container(container: LayoutContainer) -> None:
    _layout_stack.append(container)


def pop_container() -> LayoutContainer:
    return _layout_stack.pop()


@contextmanager
def vstack(
    padding: int = 8,
    spacing: int = 6,
) -> Generator[LayoutContainer, None, None]:
    """Vertical stack layout context manager."""
    container = LayoutContainer(
        kind="vstack",
        padding=padding,
        spacing=spacing,
        parent=_layout_stack[-1] if _layout_stack else None,
    )
    push_container(container)
    try:
        yield container
    finally:
        popped = pop_container()
        if popped.parent is not None:
            popped.parent.add_group(popped)  # type: ignore[attr-defined]
        else:
            get_active_window().set_root_layout(popped)


@contextmanager
def hstack(
    padding: int = 8,
    spacing: int = 6,
) -> Generator[LayoutContainer, None, None]:
    """Horizontal stack layout context manager."""
    container = LayoutContainer(
        kind="hstack",
        padding=padding,
        spacing=spacing,
        parent=_layout_stack[-1] if _layout_stack else None,
    )
    push_container(container)
    try:
        yield container
    finally:
        popped = pop_container()
        if popped.parent is not None:
            popped.parent.add_group(popped)  # type: ignore[attr-defined]


@contextmanager
def groupbox(
    title: str,
    padding: int = 10,
    spacing: int = 6,
) -> Generator[LayoutContainer, None, None]:
    """Group box container with titled border."""
    container = LayoutContainer(
        kind="groupbox",
        padding=padding,
        spacing=spacing,
        title=title,
        parent=_layout_stack[-1] if _layout_stack else None,
    )
    push_container(container)
    try:
        yield container
    finally:
        popped = pop_container()
        parent = _current_container() if _layout_stack else None
        if parent is not None:
            parent.add_group(popped)  # type: ignore[attr-defined]


def register_widget(widget: "Widget") -> "Widget":
    """Add widget to the current layout container."""
    _current_container().add(widget)
    return widget


def measure_container(
    container: LayoutContainer,
    client_width: int,
    client_height: int,
) -> None:
    """Compute slot geometry for all widgets in a container tree."""
    inner_width = max(0, client_width - 2 * container.padding)

    if container.kind == "groupbox":
        _measure_groupbox(container, inner_width)
    elif container.kind == "vstack":
        _measure_vstack(container, inner_width)
    elif container.kind == "hstack":
        _measure_hstack(container, inner_width, client_height)


def _measure_vstack(container: LayoutContainer, width: int) -> int:
    y = container.padding
    total = container.padding

    for child in container.children:
        if isinstance(child, LayoutContainer):
            child_height = _measure_groupbox(child, width) if child.kind == "groupbox" else _measure_vstack(child, width)
            child._slot = LayoutSlot(  # noqa: SLF001
                container.padding, y, width, child_height
            )
            y += child_height + container.spacing
            total = y
        else:
            h = child.preferred_height(width)
            child._slot = LayoutSlot(container.padding, y, width, h)  # noqa: SLF001
            y += h + container.spacing
            total = y

    total += container.padding
    container.measured_height = total  # type: ignore[attr-defined]
    return total


def _measure_hstack(container: LayoutContainer, width: int, height: int) -> int:
    count = len(container.children)
    if count == 0:
        return container.padding * 2

    spacing_total = container.spacing * max(0, count - 1)
    slot_width = max(20, (width - spacing_total) // max(count, 1))
    x = container.padding
    max_h = 0

    for child in container.children:
        if isinstance(child, LayoutContainer):
            h = _measure_vstack(child, slot_width)
        else:
            h = child.preferred_height(slot_width)
        child._slot = LayoutSlot(x, container.padding, slot_width, h)  # noqa: SLF001
        max_h = max(max_h, h)
        x += slot_width + container.spacing

    total = max_h + 2 * container.padding
    container.measured_height = total  # type: ignore[attr-defined]
    return total


def _measure_groupbox(container: LayoutContainer, width: int) -> int:
    # Title band + inner content
    title_height = 14
    inner_y_offset = title_height + container.padding
    inner_width = max(0, width - 2 * container.padding)
    y = inner_y_offset

    for child in container.children:
        if isinstance(child, LayoutContainer):
            h = _measure_vstack(child, inner_width)
        else:
            h = child.preferred_height(inner_width)
        child._slot = LayoutSlot(  # noqa: SLF001
            container.padding * 2, y, inner_width, h
        )
        y += h + container.spacing

    total = y + container.padding
    container.measured_height = total  # type: ignore[attr-defined]
    container._slot = LayoutSlot(  # noqa: SLF001
        container.padding, 0, width, total
    )
    return total


# Monkey-patch group support onto LayoutContainer
def _add_group(self: LayoutContainer, group: LayoutContainer) -> None:
    self.children.append(group)
    group.parent = self


LayoutContainer.add_group = _add_group  # type: ignore[attr-defined]
