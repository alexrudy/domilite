from domilite.dom_tag import dom_tag
from markupsafe import Markup


def test_name():
    div = type("div", (dom_tag,), {})
    assert div().name == "div"

    orb = type("orb_tag", (dom_tag,), {"__tagname__": "orb"})
    assert orb().name == "orb"

    bar = type("bar_", (dom_tag,), {})
    assert bar().name == "bar"


def test_children():
    a = dom_tag()
    assert len(a) == 0
    a.add(dom_tag())
    assert len(a) == 1
    child = a[0]
    assert isinstance(child, dom_tag)
    assert child.name == "dom_tag"
    a.clear()
    b = dom_tag()
    c = dom_tag()
    a.add(b, c, Markup("What"))

    assert len(a) == 3
    a.remove(b)
    assert len(a) == 2

    a[1] = b
    assert all(isinstance(child, dom_tag) for child in a)
    assert a[0] == c
