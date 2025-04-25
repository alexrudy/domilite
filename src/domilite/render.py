import io
import dataclasses as dc
import contextlib
from collections.abc import Iterator
from typing import TYPE_CHECKING

from .flags import auto, Flag

if TYPE_CHECKING:
    from domilite.dom_tag import dom_tag  # noqa F401


class RenderFlags(Flag):
    PRETTY = auto()
    XHTML = auto()


@dc.dataclass
class RenderStream:
    buffer: io.StringIO = dc.field(default_factory=io.StringIO, init=False)
    current_indent: int = dc.field(default=0, init=False)
    indent_text: str = "  "
    flags: RenderFlags = RenderFlags(0)

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
