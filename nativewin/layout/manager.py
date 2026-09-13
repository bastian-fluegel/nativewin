"""Declarative layout managers: vstack, hstack, groupbox slot positioning."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Generator, List, Optional, TYPE_CHECKING, Union

from nativewin.core import metrics

if TYPE_CHECKING:
    from nativewin.window.form import Window
    from nativewin.widgets.base import Widget

Child = Union["Widget", "LayoutContainer"]


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
    children: List[Child] = field(default_factory=list)
    parent: Optional["LayoutContainer"] = None
    measured_width: int = 0
    measured_height: int = 0
    _slot: LayoutSlot = field(default_factory=LayoutSlot)

    def add(self, widget: "Widget") -> "Widget":
        """Register a widget in this container."""
        self.children.append(widget)
        widget._container = self  # noqa: SLF001
        return widget

    def add_group(self, group: "LayoutContainer") -> None:
        self.children.append(group)
        group.parent = self


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
    padding: Optional[int] = None,
    spacing: Optional[int] = None,
) -> Generator[LayoutContainer, None, None]:
    """Vertical stack layout context manager."""
    container = LayoutContainer(
        kind="vstack",
        padding=metrics.dialog_padding() if padding is None else padding,
        spacing=metrics.dialog_spacing() if spacing is None else spacing,
        parent=_layout_stack[-1] if _layout_stack else None,
    )
    push_container(container)
    try:
        yield container
    finally:
        popped = pop_container()
        if popped.parent is not None:
            popped.parent.add_group(popped)
        else:
            get_active_window().set_root_layout(popped)


@contextmanager
def hstack(
    padding: Optional[int] = None,
    spacing: Optional[int] = None,
) -> Generator[LayoutContainer, None, None]:
    """Horizontal stack layout context manager."""
    container = LayoutContainer(
        kind="hstack",
        padding=metrics.dialog_padding() if padding is None else padding,
        spacing=metrics.dialog_spacing() if spacing is None else spacing,
        parent=_layout_stack[-1] if _layout_stack else None,
    )
    push_container(container)
    try:
        yield container
    finally:
        popped = pop_container()
        if popped.parent is not None:
            popped.parent.add_group(popped)


@contextmanager
def groupbox(
    title: str,
    padding: Optional[int] = None,
    spacing: Optional[int] = None,
) -> Generator[LayoutContainer, None, None]:
    """Group box container with titled border."""
    container = LayoutContainer(
        kind="groupbox",
        padding=metrics.group_padding() if padding is None else padding,
        spacing=metrics.dialog_spacing() if spacing is None else spacing,
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
            parent.add_group(popped)


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
    if container.kind == "groupbox":
        _measure_groupbox(container, max(0, client_width))
    elif container.kind == "vstack":
        _measure_vstack(container, max(0, client_width))
    elif container.kind == "hstack":
        _measure_hstack(container, max(0, client_width), client_height)


def _child_size(child: Child, available: int) -> tuple[int, int]:
    if isinstance(child, LayoutContainer):
        if child.kind == "groupbox":
            _measure_groupbox(child, available)
        elif child.kind == "hstack":
            _measure_hstack(child, available, 0)
        else:
            _measure_vstack(child, available)
        return child.measured_width, child.measured_height
    return child.preferred_width(available), child.preferred_height(available)


def _measure_vstack(container: LayoutContainer, width: int) -> int:
    inner = max(0, width - 2 * container.padding)
    y = container.padding
    max_w = 0

    for child in container.children:
        child_w, child_h = _child_size(child, inner)
        child._slot = LayoutSlot(container.padding, y, child_w, child_h)
        max_w = max(max_w, child_w)
        y += child_h + container.spacing

    if container.children:
        y -= container.spacing
    total_h = y + container.padding
    total_w = max_w + 2 * container.padding
    container.measured_height = total_h
    container.measured_width = total_w
    return total_h


def _measure_hstack(container: LayoutContainer, width: int, height: int) -> int:
    inner = max(0, width - 2 * container.padding)
    count = len(container.children)
    if count == 0:
        container.measured_height = container.padding * 2
        container.measured_width = container.padding * 2
        return container.measured_height

    spacing_total = container.spacing * max(0, count - 1)
    stretch: list[Child] = []
    intrinsic_total = 0
    for child in container.children:
        if isinstance(child, LayoutContainer) or getattr(child, "fills_width", True):
            stretch.append(child)
        else:
            intrinsic_total += child.preferred_width(inner)

    remain = inner - intrinsic_total - spacing_total
    stretch_unit = max(0, remain // max(len(stretch), 1)) if stretch else 0

    x = container.padding
    max_h = 0
    used_w = 0
    for child in container.children:
        if child in stretch:
            avail = stretch_unit if stretch else inner
            child_w, child_h = _child_size(child, avail)
        else:
            child_w, child_h = _child_size(child, inner)
        child._slot = LayoutSlot(x, container.padding, child_w, child_h)
        max_h = max(max_h, child_h)
        x += child_w + container.spacing
        used_w += child_w

    used_w += spacing_total
    total_h = max_h + 2 * container.padding
    container.measured_height = total_h
    container.measured_width = used_w + 2 * container.padding
    return total_h


def _measure_groupbox(container: LayoutContainer, width: int) -> int:
    title_height = metrics.group_title_band()
    inner_width = max(0, width - 2 * container.padding)
    y = title_height + container.padding
    max_w = 0

    for child in container.children:
        child_w, child_h = _child_size(child, inner_width)
        child._slot = LayoutSlot(container.padding, y, child_w, child_h)
        max_w = max(max_w, child_w)
        y += child_h + container.spacing

    if container.children:
        y -= container.spacing
    total = y + container.padding
    container.measured_height = total
    container.measured_width = max(width, max_w + 2 * container.padding)
