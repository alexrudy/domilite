from domilite.dom_tag import Flags, dom_tag
from markupsafe import Markup

import pytest

pytestmark = pytest.mark.usefixtures("tracing")


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

    with pytest.raises(IndexError):
        a[5]

    with pytest.raises(IndexError):
        a[6] = "wat"

    assert (
        a.render(pretty=False)
        == "<dom_tag><dom_tag></dom_tag><dom_tag></dom_tag></dom_tag>"
    )

    a[1] = "<>"
    assert a[1] == Markup.escape("<>")

    with pytest.raises(TypeError):
        a[1] = True  # type: ignore


def test_equality():
    b = dom_tag()
    a = dom_tag(b, foo="bar")

    assert a == dom_tag(dom_tag(), foo="bar")
    assert a != b
    assert a.__eq__(object()) == NotImplemented


def test_index():
    b = dom_tag()
    a = dom_tag(b, foo="bar")

    assert a["foo"] == "bar"
    assert a[0] == b

    with pytest.raises(TypeError):
        a[b"something"]  # type: ignore

    with pytest.raises(TypeError):
        a[b"what"] = "foo"  # type: ignore


def test_render():
    a = dom_tag()
    s = a.render()
    assert s == "<dom_tag></dom_tag>"
    assert a.render() == "<dom_tag></dom_tag>"


def test_render_pretty():
    b = dom_tag(name="b")
    a = dom_tag(b, name="a")

    assert (
        a.render() == '<dom_tag name="a">\n  <dom_tag name="b"></dom_tag>\n</dom_tag>'
    )
    assert (
        a.render(pretty=False)
        == '<dom_tag name="a"><dom_tag name="b"></dom_tag></dom_tag>'
    )
    assert (
        a.render(pretty=True)
        == '<dom_tag name="a">\n  <dom_tag name="b"></dom_tag>\n</dom_tag>'
    )
    assert (
        a.__html__() == '<dom_tag name="a">\n  <dom_tag name="b"></dom_tag>\n</dom_tag>'
    )

    class dom_single(dom_tag):
        flags = Flags.SINGLE

    s = dom_single()
    assert s.render() == "<dom_single>"
    assert s.render(xhtml=True) == "<dom_single />"
    assert s.render(xhtml=False) == "<dom_single>"

    class dom_inline(dom_tag):
        flags = Flags.INLINE

    i = dom_inline()
    c = dom_tag(i, name="c")

    assert c.render() == '<dom_tag name="c"><dom_inline></dom_inline></dom_tag>'


def test_unsupported_child():
    a = dom_tag()
    a.children.append(9)  # type: ignore

    with pytest.raises(TypeError):
        a.render()


def test_attributes():
    a = dom_tag()
    a.attributes["foo"] = "bar"
    assert a["foo"] == "bar"

    a["bar"] = "foo"
    assert a.attributes["bar"] == "foo"
    assert a.render() == '<dom_tag foo="bar" bar="foo"></dom_tag>'

    with pytest.raises(KeyError):
        a["baz"]

    with pytest.raises(TypeError):
        a["foo"] = 1  # type: ignore


def test_add_string():
    a = dom_tag("label", "<>")
    assert a.render() == "<dom_tag>label&lt;&gt;</dom_tag>"
    assert a[0] == Markup("label")
    assert a[1] == Markup.escape("<>")


def test_bool():
    a = dom_tag()
    assert bool(a) is True
    assert a
