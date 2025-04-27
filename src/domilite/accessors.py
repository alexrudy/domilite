import dataclasses as dc
import itertools
import re
import weakref
from collections.abc import Iterable
from collections.abc import Iterator
from collections.abc import MutableMapping
from collections.abc import MutableSet
from typing import ClassVar
from typing import Generic
from typing import Protocol
from typing import Self
from typing import TypeVar
from typing import overload

from domilite.render import RenderFlags
from domilite.render import RenderParts
from domilite.render import RenderStream

__all__ = [
    "ChainedMethodError",
    "Classes",
    "ClassesProperty",
    "Attributes",
    "AttributesProperty",
    "PrefixAccessor",
    "PrefixAccess",
]

S = TypeVar("S")

SPECIAL_PREFIXES = {"data", "aria", "role"}
WHITESPACE = re.compile(r"[\s]+")


class ChainedMethodError(TypeError):
    pass


@dc.dataclass(frozen=True, slots=True, repr=False)
class Classes(MutableSet[str], Generic[S]):
    """
    A set-like helper for manipulating the class attribute on a tag.

    This provides set methods and set interaction, but also correctly
    maintains and renders the whitespace delimited `class` attribute
    for an associated tag.
    """

    _tag: weakref.ReferenceType[S] = dc.field(compare=False, hash=False)
    _classes: list[str] = dc.field(default_factory=list, init=False)

    def __contains__(self, cls: object) -> bool:
        return cls in self._classes

    def __iter__(self) -> Iterator[str]:
        return iter(self._classes)

    def __len__(self) -> int:
        return len(self._classes)

    def _chain(self) -> S:
        tag = self._tag()
        if tag is not None:
            return tag
        raise ChainedMethodError("method chaining is unavailable, underlying instance is missing")

    def _validate(self, item: str) -> str:
        if (found := re.search(WHITESPACE, item)) is not None:
            raise ValueError(f"Class names cannot contain whitespace. Got: {item!r} {found!r}")
        return item

    def clear(self) -> S:  # type: ignore[override]
        self._classes.clear()
        return self._chain()

    def _replace(self, classes: Iterable[str]) -> None:
        self._classes[:] = [self._validate(item) for item in classes]

    def replace(self, *classes: str) -> S:
        """Replace a specific class.

        Returns the tag. This is useful for chaining methods on a tag.
        """
        self._replace(classes)
        return self._chain()

    def render(self) -> str:
        """Render the classes as a whitespace-separated string"""
        return " ".join(self._classes)

    def __str__(self) -> str:
        return self.render()

    def __repr__(self) -> str:
        if not self._classes:
            return "{}"
        parts = ["{"]
        parts.append(", ".join(repr(item) for item in self._classes))
        parts.append("}")
        return " ".join(parts)

    def add(self, *classes: str) -> S:  # type: ignore[override]
        """Add classes to the tag.

        Returns the tag. This is useful for chaining methods on a tag.
        """
        for cls in classes:
            cls = self._validate(cls)
            if cls not in self._classes:
                self._classes.append(cls)
        return self._chain()

    def remove(self, value: str) -> S:  # type: ignore[override]
        """Remove element elem from the set. Raises KeyError if elem is not contained in the set.

        Returns the tag. This is useful for chaining methods on a tag.
        """
        value = self._validate(value)
        if value in self._classes:
            self._classes.remove(value)
        else:
            raise KeyError(f"Class '{value}' not found")
        return self._chain()

    def discard(self, value: str) -> S:  # type: ignore[override]
        """Remove class value from the set if it is present.

        Returns the tag. This is useful for chaining methods on a tag.
        """
        value = self._validate(value)
        if value in self._classes:
            self._classes.remove(value)
        return self._chain()

    def swap(self, old: str, new: str) -> S:
        """Swap one class for another.

        Returns the tag. This is useful for chaining methods on a tag."""
        old = self._validate(old)
        new = self._validate(new)

        if old in self._classes:
            self._classes.remove(old)
        if new not in self._classes:
            self._classes.append(new)
        return self._chain()


@dc.dataclass(repr=False, frozen=True, slots=True)
class Attributes(MutableMapping[str, str | bool], Generic[S]):
    """Provides a dictionary interface to DOM element attributes.

    This interface also transparently forwards interactions with `class`
    to the `classes` object, so that classes can be managed as a set of
    strings.

    The attributes interface normalizes attribute names, transparently handles
    boolean attributes appropriately, and can render attributes to a string.

    This object should not be constructed individually, rather it should be
    accessed from the :attr:`~domilite.dom_tag.dom_tag.attributes` attribute of
    :class:`~domilite.dom_tag.dom_tag`"""

    _tag: weakref.ReferenceType[S] = dc.field(compare=False, hash=False)
    _attributes: dict[str, str] = dc.field(default_factory=dict, init=False)

    #: Access to the `class` attribute as a set of strings.
    classes: Classes[S] = dc.field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "classes", Classes(self._tag))

    @classmethod
    def from_tag(cls, tag: S) -> Self:
        """Construct an Attributes object from a tag object. Attributes
        retains a weak reference to the underlying tag."""
        return cls(weakref.ref(tag))

    def _chain(self) -> S:
        tag = self._tag()
        if tag is not None:
            return tag
        raise ChainedMethodError("method chaining is unavailable, underlying instance is missing")

    def normalize_attribute(self, attribute: str) -> str:
        """Normalize the name of an attribute."""
        # Shorthand notation
        attribute = {
            "cls": "class",
            "className": "class",
            "class_name": "class",
            "klass": "class",
            "fr": "for",
            "html_for": "for",
            "htmlFor": "for",
            "phor": "for",
        }.get(attribute, attribute)

        if attribute == "_":
            return attribute

        # Workaround for Python's reserved words
        if attribute[0] == "_":
            attribute = attribute[1:]

        if attribute[-1] == "_":
            attribute = attribute[:-1]

        if any(attribute.startswith(prefix + "_") for prefix in SPECIAL_PREFIXES):
            attribute = attribute.replace("_", "-")

        if attribute.split("_")[0] in ("xml", "xmlns", "xlink"):
            attribute = attribute.replace("_", ":")

        if (tag := self._tag()) is not None and (normalize := getattr(tag, "normalize_attribute", None)) is not None:
            attribute = normalize(attribute)

        return attribute

    def normalize_pair(self, attribute: str, value: str | bool) -> tuple[str, str | None]:
        """Normalize the name and value of an attribute, handling boolean values appropriately.

        Returning a value of `None` indicates that the attribute should be removed.
        """
        attribute = self.normalize_attribute(attribute)
        if value is True:
            value = attribute
        if value is False:
            return (attribute, None)
        return attribute, value

    def __getitem__(self, key: str) -> str | bool:
        name = self.normalize_attribute(key)
        if name == "class":
            return " ".join(self.classes)

        try:
            value = self._attributes[name]
        except KeyError:
            raise KeyError(key) from None

        if value == name:
            return True
        return value

    def __setitem__(self, key: str, value: str | bool) -> None:
        name, normalized = self.normalize_pair(key, value)

        if name == "class":
            if normalized is None:
                self.classes.clear()
            else:
                self.classes.replace(*normalized.split())
            return

        if normalized is None:
            self._attributes.pop(name, None)
        else:
            self._attributes[name] = normalized

    def __delitem__(self, key: str, /) -> None:
        name = self.normalize_attribute(key)
        if name == "class":
            self.classes.clear()
        else:
            del self._attributes[name]

    def __iter__(self) -> Iterator[str]:
        if self.classes:
            return itertools.chain(iter(self._attributes), itertools.repeat("class", 1))
        return iter(self._attributes)

    def __len__(self) -> int:
        if self.classes:
            return len(self._attributes) + 1
        return len(self._attributes)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, dict):
            return {**self._attributes, "class": " ".join(self.classes)} == other

        if not isinstance(other, Attributes):
            return NotImplemented

        return self._attributes == other._attributes and self.classes == other.classes

    def render(
        self,
        indent: str = "  ",
        flags: RenderFlags = RenderFlags.PRETTY,
        pretty: bool | None = None,
        xhtml: bool | None = None,
    ) -> str:
        """Render the attributes as a string.

        Parameters
        ----------
        indent: str, optional
            String to use for indenting in `pretty` mode. Defaults to two spaces: `  `
        flags: :class:`~domilite.render.RenderFlags`
            Adjust the rendering properties to use (e.g. turn off PRETTY)
        pretty: bool or None
            Explicitly enable or disable pretty rendering.
        xhtml: bool or None
            Explicitly enable or disable xhtml rendering.

        """
        stream = RenderStream(indent_text=indent, flags=flags.with_arguments(pretty=pretty, xhtml=xhtml))
        self._render(stream)
        return stream.getvalue()

    def _render(self, stream: RenderStream) -> None:
        items: Iterable[tuple[str, str]]
        if self.classes:
            items = itertools.chain(self._attributes.items(), (("class", self.classes.render()),))
        else:
            items = self._attributes.items()

        with stream.parts() as parts:
            for name, value in sorted(items):
                self._render_attribute(name, value, parts)

    def _render_attribute(self, name: str, value: str, parts: RenderParts) -> None:
        if name == value and not (parts.flags & RenderFlags.XHTML):
            parts.append(name)
        else:
            parts.append(f'{name}="{value}"')

    def set(self, key: str, value: str | bool) -> S:
        """Set an attribute to a value, and return the underlying tag.

        This is useful for chaining methods on a tag.
        """
        self[key] = value
        return self._chain()

    def delete(self, key: str) -> S:
        """Delete an attribute and return the underlying tag.

        This is useful for chaining methods on a tag.
        """
        del self[key]
        return self._chain()

    def __repr__(self) -> str:
        return f"Attributes({self.render()})"


@dc.dataclass()
class AttributesProperty(Generic[S]):
    """Property access to :class:`Attributes`"""

    _name: str | None = dc.field(default=None, init=False)
    _attribute: str | None = dc.field(default=None, init=False)

    def __set_name__(self, owner: type[S], name: str) -> None:
        self._name = name
        self._attribute = f"_{self._name}_inner"

    @overload
    def __get__(self, instance: S, owner: type[S] | None = None) -> "Attributes[S]": ...

    @overload
    def __get__(self, instance: None, owner: type[S] | None = None) -> "Self": ...

    def __get__(self, instance: S | None, owner: type[S] | None = None) -> "Attributes[S] | Self":
        if instance is None:
            return self
        assert isinstance(self._attribute, str), "Accessing attributes before __set_name__ was called"
        if (attributes := getattr(instance, self._attribute, None)) is not None:
            return attributes
        attributes = Attributes.from_tag(instance)
        setattr(instance, self._attribute, attributes)
        return attributes

    def classes(self) -> "ClassesProperty":
        return ClassesProperty(weakref.ref(self))


@dc.dataclass()
class ClassesProperty(Generic[S]):
    """Property access to :class:`Classes`"""

    _attributes: weakref.ReferenceType[AttributesProperty[S]]

    @overload
    def __get__(self, instance: S, owner: type[S]) -> "Classes[S]": ...

    @overload
    def __get__(self, instance: None, owner: type[S]) -> "Self": ...

    def __get__(self, instance: S | None, owner: type[S]) -> "Classes[S] | Self":
        if instance is None:
            return self
        attributes = self._attributes()
        if attributes is None:
            raise ValueError("Attributes has been garbage collected")
        return attributes.__get__(instance, owner).classes


class _HasAttributes(Protocol):
    @property
    def attributes(self) -> MutableMapping[str, str | bool]: ...


class _HasAttributesProperty(Protocol):
    attributes: ClassVar[AttributesProperty]


T = TypeVar("T", bound="_HasAttributesProperty | _HasAttributes")


@dc.dataclass(frozen=True)
class PrefixAccessor(Generic[T]):
    """A helper property for accessing attributes with a prefix.

    See :class:`PrefixAccess`"""

    #: Attribute prefix
    prefix: str

    @overload
    def __get__(self, instance: T, owner: type[T]) -> "PrefixAccess": ...

    @overload
    def __get__(self, instance: None, owner: type[T]) -> "Self": ...

    def __get__(self, instance: T | None, owner: type[T]) -> "PrefixAccess | Self":
        if instance is None:
            return self
        return PrefixAccess(self.prefix, instance)


@dc.dataclass(frozen=True, slots=True)
class PrefixAccess(MutableMapping[str, str | bool], Generic[T]):
    """Provide access to attributes automatically prefixed with some value.

    For example, a prefix accessor for `aria` provides access to keys like `current-page`
    which when rendered will be rendered as `aria-current-page`.

    """

    #: Attribute prefix
    prefix: str

    #: The tag to access
    tag: T

    def __getitem__(self, name: str) -> str | bool:
        return self.tag.attributes[f"{self.prefix}-{name}"]

    def __setitem__(self, name: str, value: str | bool) -> None:
        self.tag.attributes[f"{self.prefix}-{name}"] = value

    def __delitem__(self, name: str) -> None:
        del self.tag.attributes[f"{self.prefix}-{name}"]

    def __iter__(self) -> Iterator[str]:
        for key in self.tag.attributes:
            if key.startswith(f"{self.prefix}-"):
                yield key[len(self.prefix) + 1 :]

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def set(self, name: str, value: str | bool) -> T:
        """Set an attribute with the given name.

        This is useful for chaining methods on a tag.
        """
        self[name] = value
        return self.tag

    def remove(self, name: str) -> T:
        """Remove an attribute with the given name.

        This is useful for chaining methods on a tag.
        """
        del self[name]
        return self.tag
