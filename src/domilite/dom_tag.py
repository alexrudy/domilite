import contextlib
import sys
from collections.abc import Iterator
from enum import auto
from typing import TYPE_CHECKING, ClassVar
from typing import overload

from markupsafe import Markup

from .render import RenderFlags, RenderStream
from .flags import Flag
from .accessors import AttributesProperty

if not TYPE_CHECKING and sys.version_info < (3, 5, 2):  # pragma: no cover

    def overload(f):
        return f


class Flags(Flag):
    SINGLE = auto()
    PRETTY = auto()
    INLINE = auto()


def _trace_live(msg: str) -> None:
    import inspect
    import logging

    logger = logging.getLogger()

    stack = inspect.stack()
    frame = stack[1]
    self = frame.frame.f_locals.get("self", None)
    name = getattr(self, "name", "unknown")
    logger.debug(
        f"[<{name}>:{frame.filename}:{frame.lineno} in {frame.function}] {msg}"
    )


def _trace_noop(msg: str) -> None:  # pragma: no cover
    pass


_trace = _trace_noop


@contextlib.contextmanager
def render_tracing() -> Iterator[None]:
    global _trace
    try:
        _trace = _trace_live
        yield
    finally:
        _trace = _trace_noop


class dom_tag:
    __slots__ = ("_attributes_inner", "children", "__weakref__")

    flags: ClassVar["Flags"] = Flags.PRETTY

    attributes: AttributesProperty["dom_tag"] = AttributesProperty()
    classes = attributes.classes()
    children: list["dom_tag | Markup"]

    def __init__(self, *args: "str | dom_tag | Markup", **kwargs: str | bool) -> None:
        self.attributes.update(kwargs)
        self.children = []
        self.add(*args)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, dom_tag):
            return NotImplemented

        return (
            (self.name == other.name)
            and (self.attributes == other.attributes)
            and (self.children == other.children)
        )

    @property
    def name(self) -> str:
        name = getattr(self, "__tagname__", type(self).__name__)
        if name[-1] == "_":
            name = name[:-1]
        return name

    def add(self, *children: "dom_tag | str | Markup") -> "dom_tag":
        for child in children:
            if isinstance(child, str):
                child = Markup.escape(child)
            self.children.append(child)
        return self

    def remove(self, child: "dom_tag | Markup") -> "dom_tag":
        self.children.remove(child)
        return self

    def clear(self) -> "dom_tag":
        self.children.clear()
        return self

    @overload
    def __getitem__(self, index: int) -> "dom_tag | Markup": ...

    @overload
    def __getitem__(self, index: str) -> "str | bool": ...  # noqa: F811

    def __getitem__(self, index: int | str) -> "dom_tag | Markup | str | bool":  # noqa: F811
        if isinstance(index, int):
            try:
                return self.children[index]
            except IndexError:
                raise IndexError(f"Index for children out of range: {index}")
        elif isinstance(index, str):
            try:
                return self.attributes[index]
            except KeyError:
                raise KeyError(f"Attribute not found: {index}")
        raise TypeError(f"Invalid index type: {type(index)}")

    @overload
    def __setitem__(self, index: int, value: "str |dom_tag | Markup") -> None: ...

    @overload
    def __setitem__(self, index: str, value: "str | bool") -> None: ...  # noqa: F811

    def __setitem__(  # noqa: F811
        self, index: int | str, value: "str | bool | dom_tag | Markup"
    ) -> None:
        if isinstance(index, int):
            if isinstance(value, str):
                value = Markup.escape(value)
            elif isinstance(value, bool):
                raise TypeError(f"Invalid child type: {type(value)}")

            try:
                self.children[index] = value
            except IndexError:
                raise IndexError(f"Index for children out of range: {index}")
        elif isinstance(index, str):
            if not isinstance(value, (str, bool)):
                raise TypeError(f"Invalid value type for attribute: {type(value)}")

            self.attributes[index] = value
        else:
            raise TypeError(f"Invalid index type: {type(index)}")

    def __iter__(self) -> Iterator["dom_tag | Markup"]:
        return iter(self.children)

    def __len__(self) -> int:
        return len(self.children)

    def __bool__(self) -> bool:
        return True

    __nonzero__ = __bool__

    def render(
        self,
        indent: str = "  ",
        flags: RenderFlags = RenderFlags.PRETTY,
        pretty: bool | None = None,
        xhtml: bool | None = None,
    ) -> str:
        """Render this tree of tags to a string.

        Parameters
        ----------
        indent: str, optional
            String to use for indenting in `pretty` mode. Defaults to two spaces: `  `

        """
        if pretty is True:
            flags |= RenderFlags.PRETTY
        elif pretty is False:
            flags &= ~RenderFlags.PRETTY
        if xhtml is True:
            flags |= RenderFlags.XHTML
        elif xhtml is False:
            flags &= ~RenderFlags.XHTML

        stream = RenderStream(indent, flags)
        _trace(f"_render {flags}")
        self._render(stream)
        return stream.getvalue()

    def __str__(self) -> str:
        return self.render()

    def __html__(self) -> str:
        return self.render()

    def _render(self, stream: RenderStream) -> None:
        pretty = stream.flags.is_pretty and self.flags.is_pretty

        _trace("open <")
        stream.write("<")
        stream.write(self.name)

        if self.attributes:
            _trace(f"attributes {len(self.attributes)}")
            stream.write(" ")
            stream.write(self.attributes.render())

        if (self.flags & Flags.SINGLE) and (stream.flags & RenderFlags.XHTML):
            _trace("open single xhtml />")
            stream.write(" />")
        else:
            _trace("open tag >")
            stream.write(">")

        if self.flags & Flags.SINGLE:
            return

        with stream.indented():
            _trace(f"children: {len(self.children)}")
            inline = self._render_children(stream)

        if pretty and not inline:
            stream.newline()
        _trace("close tag </ >")
        stream.write(f"</{self.name}>")
        return

    def _render_children(self, stream: RenderStream) -> bool:
        inline = True
        for child in self.children:
            if isinstance(child, dom_tag):
                if (
                    RenderFlags.PRETTY in stream.flags
                ) and Flags.INLINE not in child.flags:
                    _trace("newline()")
                    inline = False
                    stream.newline()
                _trace(f"_render {child.name}")
                child._render(stream)
            elif isinstance(child, Markup):
                _trace("write")
                stream.write(child)
            else:
                raise TypeError(f"Unsupported child type: {type(child)}")
        return inline

    def __repr__(self) -> str:
        parts = [f"{type(self).__module__}.{self.name}"]

        if self.attributes:
            if len(self.attributes) == 1:
                parts.append("1 attribute")
            else:
                parts.append(f"{len(self.attributes)} attributes")

        if self.children:
            if len(self.children) == 1:
                parts.append("1 child")
            else:
                parts.append(f"{len(self.children)} children")

        return "<" + " ".join(parts) + ">"
