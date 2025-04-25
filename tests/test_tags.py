"""Test specific HTML tags"""

from markupsafe import Markup
from domilite import tags


def test_title_ignores_childtags():
    title = tags.title("hello", tags.span(" world wide"), " web")
    assert title.text == "hello web"

    title.text = "Goodbye"
    assert title.text == "Goodbye"
    assert title.children == [Markup("Goodbye")]
