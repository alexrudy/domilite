"""Test specific HTML tags"""

import pytest
from markupsafe import Markup
from domilite import tags


def test_title_ignores_childtags():
    title = tags.title("hello", tags.span(" world wide"), " web")
    assert title.text == "hello web"

    title.text = "Goodbye"
    assert title.text == "Goodbye"
    assert title.children == [Markup("Goodbye")]


def test_comment_tag():
    comment = tags.comment("hello", tags.div("world"))

    assert comment.render() == "<!--hello\n  <div>world</div>\n-->"


def test_comment_nesting():
    comment = tags.comment("hello", tags.div("world"))
    comment.add(tags.comment("child"))

    with pytest.raises(ValueError):
        comment.render()
