from collections.abc import Iterator
import pytest
from domilite.dom_tag import render_tracing


@pytest.fixture
def tracing() -> Iterator[None]:
    with render_tracing():
        yield
