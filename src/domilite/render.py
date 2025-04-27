import contextlib
import dataclasses as dc
import io
from collections.abc import Iterator
from typing import TYPE_CHECKING

from .flags import Flag
from .flags import auto

if TYPE_CHECKING:
    from domilite.dom_tag import dom_tag  # noqa F401

__all__ = ["RenderFlags"]


class RenderFlags(Flag):
    """Settings for rendering tags"""

    #: Render tags with indentation across multiple lines.
    PRETTY = auto()

    #: Use XHTML semantics.
    XHTML = auto()


class ContextFlags(Flag):
    #: Currently rendering a comment, don't render sub-comments
    COMMENT = auto()


@dc.dataclass
class RenderStream:
    buffer: io.StringIO = dc.field(default_factory=io.StringIO, init=False)
    current_indent: int = dc.field(default=0, init=False)
    indent_text: str = "  "
    flags: RenderFlags = RenderFlags(0)
    context: ContextFlags = ContextFlags(0)

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

    @contextlib.contextmanager
    def comment(self) -> Iterator[None]:
        is_comment = self.context & ContextFlags.COMMENT

        self.context |= ContextFlags.COMMENT
        yield
        if not is_comment:
            self.context &= ~ContextFlags.COMMENT

    @contextlib.contextmanager
    def parts(self, joiner: str = " ") -> Iterator["RenderParts"]:
        parts = RenderParts(self, joiner=joiner)
        yield parts
        parts.close()


@dc.dataclass
class RenderParts:
    stream: RenderStream
    joiner: str = " "
    parts: list[str] = dc.field(default_factory=list, init=False)

    @property
    def flags(self) -> RenderFlags:
        return self.stream.flags

    def append(self, item: str) -> None:
        self.parts.append(item)

    def prepend(self, item: str) -> None:
        self.parts.insert(0, item)

    def close(self) -> None:
        self.stream.write(self.joiner.join(self.parts))
