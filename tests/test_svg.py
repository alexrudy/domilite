import pytest
from domilite import svg


@pytest.mark.parametrize(
    "attribute, expected",
    [
        ("foo", "foo"),
        ("class_", "class"),
        ("x_b", "x-b"),
        ("_", "_"),
    ],
)
def test_normalize_attribute(attribute: str, expected: str) -> None:
    tag = svg.svg()

    assert tag.attributes.normalize_attribute(attribute) == expected
