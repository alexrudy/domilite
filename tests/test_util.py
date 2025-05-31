from domilite.tags import a
from domilite.tags import p
from domilite.util import container


def test_container() -> None:
    c = container(p("hello", a("your name", href="https://example.com"), "!"))

    assert c.render() == '\n<p>hello\n  <a href="https://example.com">your name</a>!\n</p>\n'
