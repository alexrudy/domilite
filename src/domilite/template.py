import dataclasses as dc
from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import TypeVar

from domilite.accessors import AttributesProperty
from domilite.accessors import ClassesProperty
from domilite.accessors import PrefixAccessor
from domilite.tags import html_tag

H = TypeVar("H", bound=html_tag)


@dc.dataclass(init=False, eq=False)
class TagTemplate(Generic[H]):
    """A helper for creating tags.

    Holds the tag type as well as attributes for the tag. This can be used
    by calling the instance as a function to create a tag, or by calling the
    :meth:`update` method to apply the attributes to an existing tag.
    """

    #: The tag type
    tag: type[H]

    attributes: ClassVar[AttributesProperty["TagTemplate"]] = AttributesProperty()
    classes: ClassVar[ClassesProperty["TagTemplate"]] = attributes.classes()

    data: PrefixAccessor["TagTemplate"] = PrefixAccessor("data")
    aria: PrefixAccessor["TagTemplate"] = PrefixAccessor("aria")
    hx: PrefixAccessor["TagTemplate"] = PrefixAccessor("hx")

    def __init__(
        self, tag: type[H], attributes: Mapping[str, str | bool] | None = None, classes: Iterable[str] | None = None
    ) -> None:
        self.tag = tag
        if attributes is not None:
            self.attributes.update(attributes)
        if classes is not None:
            self.classes.add(*classes)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, html_tag):
            return self.tag is type(other) and self.attributes == other.attributes
        if isinstance(other, TagTemplate):
            return self.tag is other.tag and self.attributes == other.attributes
        return NotImplemented

    def __tag__(self) -> H:
        """Create a tag from the attributes and classes."""
        tag = self.tag(**self.attributes)
        tag.classes.add(*self.classes)
        return tag

    def __call__(self, *args: Any, **kwds: Any) -> H:
        """Create a tag from the attributes and classes.

        This method is a convenience wrapper around :meth:`__tag__` that allows
        the tag to be created with additional arguments and keyword arguments passed
        to the tag constructor.
        """
        tag = self.tag(*args, **{**self.attributes, **kwds})
        tag.classes.add(*self.classes)
        return tag

    def __setitem__(self, name: str, value: str) -> None:
        self.attributes[name] = value

    def __getitem__(self, name: str) -> str | bool:
        return self.attributes[name]

    def update(self, tag: H) -> H:
        """Update the tag with the attributes and classes."""
        tag.classes.add(*self.classes)
        tag.attributes.update(self.attributes)
        return tag
