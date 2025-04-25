from collections.abc import Iterator
import weakref
import pytest

from domilite.dom_tag import dom_tag
from domilite.accessors import (
    Attributes,
    AttributesProperty,
    ClassesProperty,
    ChainedMethodError,
    Classes,
)
from domilite.tags import html_tag


@pytest.fixture
def tag() -> Iterator[dom_tag]:
    tag_instance = dom_tag()
    yield tag_instance

    # Explicitly cleanup, so tag remains until finalizer
    del tag_instance


@pytest.fixture
def html() -> Iterator[html_tag]:
    tag_instance = html_tag()
    yield tag_instance

    # Explicitly cleanup, so tag remains until finalizer
    del tag_instance


@pytest.fixture
def attributes(tag: dom_tag) -> Iterator[Attributes]:
    yield tag.attributes


@pytest.fixture
def classes(tag: dom_tag):
    return tag.classes


def test_classes_remove_replace(classes: Classes):
    assert classes.replace(" ".join(["one", "two", "three"]))

    assert classes.render() == "one two three"
    classes.add("four")
    assert list(classes) == ["one", "two", "three", "four"]

    classes.add("four")
    assert len(classes) == 4

    assert "four" in classes
    assert "five" not in classes

    classes.remove("four")
    assert list(classes) == ["one", "two", "three"]

    with pytest.raises(KeyError):
        classes.remove("four")

    classes.discard("four")
    assert list(classes) == ["one", "two", "three"]

    classes.discard("one")
    assert list(classes) == ["two", "three"]


def test_classes_clear(classes: Classes) -> None:
    classes.add("one", "two", "three")
    assert len(classes) == 3
    classes.clear()
    assert len(classes) == 0


def test_classes_swap(classes: Classes) -> None:
    classes.add("one", "two", "three")
    classes.swap("one", "four")
    assert list(classes) == ["two", "three", "four"]
    classes.swap("one", "four")
    assert list(classes) == ["two", "three", "four"]


def test_chaining_classes(attributes: Attributes, classes: Classes) -> None:
    classes.add("one", "two", "three").classes.swap("three", "four").classes.remove(
        "two"
    ).classes.discard("five").classes.discard("four")


def test_chaining_breaking_classes() -> None:
    cl = Classes(weakref.ref(dom_tag()))
    with pytest.raises(ChainedMethodError):
        cl.add("one")


def test_chaining_attrs(tag: dom_tag) -> None:
    tag.attributes.set("foo", "bar").attributes.delete("foo")


def test_chaining_breaking_attrs() -> None:
    cl = Attributes(weakref.ref(dom_tag()))
    with pytest.raises(ChainedMethodError):
        cl.set("one", "two")


@pytest.mark.parametrize(
    "value, expected",
    [
        ("foo", "foo"),
        ("htmlFor", "for"),
        ("cls", "class"),
        ("aria_selected", "aria-selected"),
        ("_del", "del"),
        ("class_", "class"),
        ("xmlns_foo", "xmlns:foo"),
    ],
)
def test_normalize_attribute(attributes, value, expected):
    assert attributes.normalize_attribute(value) == expected


def test_tag_with_normailzer():
    class silly_tag(dom_tag):
        def normalize_attribute(self, value: str) -> str:
            return value.upper()

    tag = silly_tag()
    assert tag.attributes.normalize_attribute("foo") == "FOO"


@pytest.mark.parametrize(
    "attribute, value, expected",
    [("disabled", True, "disabled"), ("disabled", False, None)],
)
def test_normalize_pair(attributes: Attributes, attribute, value, expected):
    name, output = attributes.normalize_pair(attribute, value)
    assert attribute == name
    assert output == expected


def test_get_classes(attributes: Attributes, classes: Classes):
    classes.add("one", "two")
    assert attributes["class"] == "one two"


def test_getsetdel_truthy_value(attributes: Attributes):
    attributes["enabled"] = True
    assert attributes["enabled"] is True

    attributes["enabled"] = False
    assert "enabled" not in attributes

    attributes["enabled"] = True
    del attributes["enabled"]

    assert "enabled" not in attributes


def test_clear_class_attribute(attributes: Attributes, classes: Classes):
    classes.add("one", "two")
    assert len(classes) == 2
    attributes["class"] = False
    assert len(classes) == 0

    attributes["class"] = "three four"
    assert set(classes) == {"three", "four"}

    del attributes["class"]
    assert len(classes) == 0


def test_iteration(attributes: Attributes, classes: Classes):
    assert list(attributes) == []

    classes.add("one")
    assert list(attributes) == ["class"]

    attributes["enabled"] = "yes"
    assert list(attributes) == ["enabled", "class"]

    attributes["class"] = False
    assert list(attributes) == ["enabled"]


def test_attributes_render(attributes: Attributes, classes: Classes) -> None:
    attributes["foo"] = "bar"
    assert attributes.render() == 'foo="bar"'

    classes.add("one", "two")
    assert attributes.render() == 'foo="bar" class="one two"'


def test_attributes_equal(attributes: Attributes) -> None:
    # use a separate tag, attributes don't compare the underlying tag.
    tag = dom_tag()
    other = Attributes(weakref.ref(tag))

    assert attributes == other

    attributes["foo"] = "bar"
    other["foo"] = "bar"

    assert attributes == other

    attributes.classes.add("one", "two")
    other.classes.add("one", "two")

    assert attributes == other

    assert attributes == {"foo": "bar", "class": "one two"}

    assert attributes != 1


def test_attributes_property_get() -> None:
    prop = AttributesProperty()
    assert prop.__get__(None, dom_tag) is prop


def test_classes_property() -> None:
    attrs = AttributesProperty()
    prop = ClassesProperty(weakref.ref(attrs))

    assert prop.__get__(None, dom_tag) == prop

    tag = dom_tag()
    attrs.__set_name__(dom_tag, "attributes")
    assert isinstance(prop.__get__(tag, dom_tag), Classes)

    del attrs
    with pytest.raises(ValueError):
        prop.__get__(tag, dom_tag)


def test_prefix_accessor(html: html_tag) -> None:
    html.hx["foo"] = "bar"
    assert html.attributes["hx-foo"] == "bar"
    html.attributes["hx-bar"] = "foo"
    assert html.hx["bar"] == "foo"

    html.attributes["baz"] = "baz"
    assert len(html.hx) == 2
    assert set(html.hx) == {"foo", "bar"}

    del html.hx["foo"]

    assert "foo" not in html.hx
    assert "hx-foo" not in html.attributes

    html.hx.set("foo", "bar").hx.remove("bar")
    assert set(html.hx) == {"foo"}
