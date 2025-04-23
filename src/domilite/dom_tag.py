import contextlib
import dataclasses as dc
import enum
import sys
import io
from collections.abc import Iterator
from enum import auto
from typing import TYPE_CHECKING, ClassVar
from typing import overload

from markupsafe import Markup

if not TYPE_CHECKING and sys.version_info < (3, 5, 2):

    def overload(f):
        return f


class Flags(enum.Flag):
    SINGLE = auto()
    PRETTY = auto()
    INLINE = auto()


SPECIAL_PREFIXES = ("data-", "aria-", "role-")


class dom_tag:
    __slots__ = ("attributes", "children")

    flags: ClassVar["Flags"] = Flags.PRETTY

    attributes: dict[str, str | bool]
    children: list["dom_tag | Markup"]

    def __init__(self, *args: "str | dom_tag | Markup", **kwargs: str | bool) -> None:
        self.attributes = dict(**kwargs)
        self.children = []
        self.add(*args)

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

    def remove(self, child: "dom_tag | str | Markup") -> "dom_tag":
        if isinstance(child, str):
            child = Markup.escape(child)
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
    def __setitem__(self, index: str, value: "str") -> None: ...  # noqa: F811

    def __setitem__(self, index: int | str, value: "str | dom_tag | Markup") -> None:  # noqa: F811
        if isinstance(index, int):
            if isinstance(value, str):
                value = Markup.escape(value)
            try:
                self.children[index] = value
            except IndexError:
                raise IndexError(f"Index for children out of range: {index}")
        elif isinstance(index, str):
            if not isinstance(value, str):
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

    @staticmethod
    def normalize_attribute(attribute: str) -> str:
        """Converts attribute names to their normalized form."""
        # Shorthand notation
        attribute = {
            "cls": "class",
            "className": "class",
            "class_name": "class",
            "klass": "class",
            "fr": "for",
            "html_for": "for",
            "htmlFor": "for",
            "phor": "for",
        }.get(attribute, attribute)

        # Workaround for Python's reserved words
        if attribute[0] == "_":
            attribute = attribute[1:]

        if attribute[-1] == "_":
            attribute = attribute[:-1]

        if any(
            attribute.startswith(prefix.replace("-", "_"))
            for prefix in SPECIAL_PREFIXES
        ):
            attribute = attribute.replace("_", "-")

        if attribute.split("_")[0] in ("xml", "xmlns", "xlink"):
            attribute = attribute.replace("_", ":")

        return attribute

    @classmethod
    def normalize_pair(
        cls, attribute: str, value: str | bool
    ) -> tuple[str, str | bool]:
        attribute = cls.normalize_attribute(attribute)
        if value is True:
            value = attribute
        return attribute, value

    def render(
        self, indent: str = "  ", pretty: bool = True, xhtml: bool = False
    ) -> str:
        stream = _RenderStream(indent, pretty, xhtml)
        self._render(stream)
        return stream.getvalue()

    def __str__(self) -> str:
        return self.render()

    def _render(self, stream: "_RenderStream") -> "_RenderStream":
        pretty = stream.is_pretty and (Flags.PRETTY in self.flags)

        stream.write("<")
        stream.write(self.name)

        attributes = []

        for attribute, value in self.attributes.items():
            attribute, value = self.normalize_pair(attribute, value)
            if value is False:
                continue
            if isinstance(value, str):
                value = Markup.escape(value)
            elif not isinstance(value, Markup):
                value = Markup.escape(str(value))
            attributes.append(f'{attribute}="{value}"')

        stream.write(" ".join(attributes))

        if Flags.SINGLE in self.flags and stream.xhtml:
            stream.write(" />")
        else:
            stream.write(">")

        if Flags.SINGLE in self.flags:
            return stream

        with stream.indented():
            inline = self._render_children(stream)

        if pretty and not inline:
            stream.newline()
        stream.write(f"</{self.name}>")

        return stream

    def _render_children(self, stream: "_RenderStream") -> bool:
        inline = True
        for child in self.children:
            if isinstance(child, self.__class__):
                if stream.is_pretty and Flags.INLINE not in child.flags:
                    inline = False
                    stream.newline()
                child._render(stream)
            elif isinstance(child, Markup):
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


@dc.dataclass
class _RenderStream:
    buffer: io.StringIO = dc.field(default=io.StringIO(), init=False)
    current_indent: int = dc.field(default=0, init=False)
    indent_text: str = "  "
    xhtml: bool = False
    is_pretty: bool = False

    def write(self, text: str) -> None:
        for i, line in enumerate(text.splitlines()):
            if i:
                self.newline()
            self.buffer.write(line)

    def newline(self) -> None:
        self.buffer.write("\n" + self.indent_text * self.current_indent)

    def getvalue(self) -> str:
        return self.buffer.getvalue()

    @contextlib.contextmanager
    def indented(self) -> Iterator[None]:
        self.current_indent += 1
        yield
        self.current_indent -= 1
