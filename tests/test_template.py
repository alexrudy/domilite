import pytest

from domilite.tags import div
from domilite.tags import span
from domilite.template import TagTemplate


class TestTagTemplate:
    @pytest.fixture
    def template(self):
        return TagTemplate(div)

    @pytest.fixture
    def template_with_data(self):
        return TagTemplate(div, attributes={"id": "test", "disabled": True}, classes=["btn", "primary"])

    def test_basic_template_creation(self, template):
        assert template.tag is div
        assert len(template.attributes) == 0
        assert len(template.classes) == 0

    def test_template_with_initial_data(self, template_with_data):
        assert template_with_data.tag is div
        assert template_with_data.attributes["id"] == "test"
        assert template_with_data.attributes["disabled"] is True
        assert set(template_with_data.classes) == {"btn", "primary"}

    def test_repr_empty_template(self, template):
        assert repr(template) == f"<TagTemplate {repr(div)}>"

    def test_repr_with_attributes_and_classes(self, template_with_data):
        repr_str = repr(template_with_data)
        assert "TagTemplate" in repr_str
        assert repr(div) in repr_str
        assert "3 attributes" in repr_str
        assert "2 classes" in repr_str

    def test_getitem_setitem(self, template):
        template["foo"] = "bar"
        assert template["foo"] == "bar"
        assert template.attributes["foo"] == "bar"

    def test_getitem_missing_key(self, template):
        with pytest.raises(KeyError):
            template["missing"]

    def test_tag_creation_via_call(self, template_with_data):
        tag = template_with_data()
        assert isinstance(tag, div)
        assert tag.attributes["id"] == "test"
        assert tag.attributes["disabled"] is True
        assert set(tag.classes) == {"btn", "primary"}

    def test_tag_creation_with_additional_args(self, template_with_data):
        tag = template_with_data("content", class_="extra", name="override")
        assert isinstance(tag, div)
        assert tag[0] == "content"
        assert "extra" in tag.classes
        assert "btn" in tag.classes
        assert "primary" in tag.classes
        assert tag.attributes["id"] == "test"
        assert tag.attributes["name"] == "override"

    def test_tag_creation_via_dunder_tag(self, template_with_data):
        tag = template_with_data.__tag__()
        assert isinstance(tag, div)
        assert tag.attributes["id"] == "test"
        assert set(tag.classes) == {"btn", "primary"}

    def test_update_existing_tag(self, template_with_data):
        existing_tag = span("content", class_="existing", data_value="original")
        updated_tag = template_with_data.update(existing_tag)

        assert updated_tag is existing_tag
        assert updated_tag[0] == "content"
        assert set(updated_tag.classes) == {"btn", "primary"}
        assert updated_tag.attributes["id"] == "test"
        assert updated_tag.attributes["data-value"] == "original"
        assert updated_tag.attributes["disabled"] is True

    def test_equality_with_dom_tag(self, template):
        template["foo"] = "bar"
        template.classes.add("test")

        tag = div(foo="bar", class_="test")
        assert template == tag

    def test_equality_with_different_tag_type(self, template):
        template["foo"] = "bar"
        tag = span(foo="bar")
        assert template != tag

    def test_equality_with_different_attributes(self, template):
        template["foo"] = "bar"
        tag = div(foo="baz")
        assert template != tag

    def test_equality_with_another_template(self):
        template1 = TagTemplate(div, attributes={"foo": "bar"}, classes=["test"])
        template2 = TagTemplate(div, attributes={"foo": "bar"}, classes=["test"])
        assert template1 == template2

    def test_equality_with_different_template_tag(self):
        template1 = TagTemplate(div, attributes={"foo": "bar"})
        template2 = TagTemplate(span, attributes={"foo": "bar"})
        assert template1 != template2

    def test_equality_with_unsupported_type(self, template):
        assert template != "string"
        assert template != 42
        assert template != {}

    def test_prefix_accessors_data(self, template):
        template.data["value"] = "test"
        assert template.attributes["data-value"] == "test"
        assert template.data["value"] == "test"

    def test_prefix_accessors_aria(self, template):
        template.aria["label"] = "button"
        assert template.attributes["aria-label"] == "button"
        assert template.aria["label"] == "button"

    def test_prefix_accessors_hx(self, template):
        template.hx["get"] = "/api/data"
        assert template.attributes["hx-get"] == "/api/data"
        assert template.hx["get"] == "/api/data"

    def test_prefix_accessor_deletion(self, template):
        template.hx["post"] = "/submit"
        assert "hx-post" in template.attributes
        del template.hx["post"]
        assert "hx-post" not in template.attributes

    def test_classes_attribute_interaction(self, template):
        template.classes.add("one", "two")
        template.attributes["class"] = "three four"
        assert set(template.classes) == {"three", "four"}

        tag = template()
        assert set(tag.classes) == {"three", "four"}

    def test_template_does_not_modify_class_during_creation(self):
        template = TagTemplate(div, classes=["initial"])

        tag1 = template()
        tag1.classes.add("extra")

        tag2 = template()
        assert "extra" not in tag2.classes
        assert "initial" in tag2.classes

    def test_template_preserves_boolean_attributes(self, template):
        template["disabled"] = True
        template["hidden"] = False

        tag = template()
        assert tag.attributes["disabled"] is True
        assert "hidden" not in tag.attributes

    def test_complex_template_scenario(self):
        button_template = TagTemplate(
            div, attributes={"role": "button", "tabindex": "0"}, classes=["btn", "btn-primary"]
        )

        button_template.data["action"] = "submit"
        button_template.aria["label"] = "Submit form"
        button_template["type"] = "button"

        button = button_template("Click me", class_="large", data_id="btn1")

        assert button[0] == "Click me"
        assert set(button.classes) == {"btn", "btn-primary", "large"}
        assert button.attributes["role"] == "button"
        assert button.attributes["data-action"] == "submit"
        assert button.attributes["aria-label"] == "Submit form"
        assert button.attributes["type"] == "button"
        assert button.attributes["data-id"] == "btn1"

    def test_template_chaining(self, template):
        template.classes.add("one").classes.add("two")
        template.attributes.set("foo", "bar").attributes.set("baz", "qux")

        assert set(template.classes) == {"one", "two"}
        assert template.attributes["foo"] == "bar"
        assert template.attributes["baz"] == "qux"

    def test_generic_type_preservation(self):
        span_template = TagTemplate(span)
        created_tag = span_template()
        assert isinstance(created_tag, span)
        assert type(created_tag) is span
