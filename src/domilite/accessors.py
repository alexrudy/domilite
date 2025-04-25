import dataclasses as dc
import weakref
import itertools
from collections.abc import Iterator, Iterable
from collections.abc import MutableMapping
from collections.abc import MutableSet
from typing import TYPE_CHECKING, Protocol, Self, overload
from typing import TypeVar
from typing import Generic

from domilite.render import RenderFlags, RenderStream, RenderParts

if TYPE_CHECKING:
    from .dom_tag import dom_tag

S = TypeVar("S")

SPECIAL_PREFIXES = {"data", "aria", "role"}


class ChainedMethodError(TypeError):
    pass


@dc.dataclass(frozen=True, slots=True, repr=False)
class Classes(MutableSet[str], Generic[S]):
    """A helper for manipulating the class attribute on a tag."""

    tag: weakref.ReferenceType[S] = dc.field(compare=False, hash=False)
    classes: list[str] = dc.field(default_factory=list, init=False)

    def __contains__(self, cls: object) -> bool:
        return cls in self.classes

    def __iter__(self) -> Iterator[str]:
        return iter(self.classes)

    def __len__(self) -> int:
        return len(self.classes)

    def _chain(self) -> S:
        tag = self.tag()
        if tag is not None:
            return tag
        raise ChainedMethodError("method chaining is unavailable, underlying instance is missing")

    def clear(self) -> S:  # type: ignore[override]
        self.classes.clear()
        return self._chain()

    def _replace(self, classes: list[str]) -> None:
        self.classes[:] = classes

    def replace(self, classes: str) -> S:
        self._replace(classes.split())
        return self._chain()

    def render(self) -> str:
        return " ".join(self.classes)

    def __str__(self) -> str:
        return self.render()

    def __repr__(self) -> str:
        if not self.classes:
            return "{}"
        parts = ["{"]
        parts.append(", ".join(repr(item) for item in self.classes))
        parts.append("}")
        return " ".join(parts)

    def add(self, *classes: str) -> S:  # type: ignore[override]
        """Add classes to the tag."""
        current: list[str] = self.classes
        for cls in classes:
            if cls not in current:
                current.append(cls)
        return self._chain()

    def remove(self, value: str) -> S:  # type: ignore[override]
        """Remove element elem from the set. Raises KeyError if elem is not contained in the set."""
        if value in self.classes:
            self.classes.remove(value)
        else:
            raise KeyError(f"Class '{value}' not found")
        return self._chain()

    def discard(self, value: str) -> S:  # type: ignore[override]
        """Remove class value from the set if it is present."""
        if value in self.classes:
            self.classes.remove(value)
        return self._chain()

    def swap(self, old: str, new: str) -> S:
        """Swap one class for another."""
        if old in self.classes:
            self.classes.remove(old)
        if new not in self.classes:
            self.classes.append(new)
        return self._chain()


@dc.dataclass(repr=False, frozen=True, slots=True)
class Attributes(MutableMapping[str, str | bool], Generic[S]):
    tag: weakref.ReferenceType[S] = dc.field(compare=False, hash=False)
    attributes: dict[str, str] = dc.field(default_factory=dict, init=False)
    classes: Classes[S] = dc.field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "classes", Classes(self.tag))

    @classmethod
    def from_tag(cls, tag: S) -> Self:
        return cls(weakref.ref(tag))

    def _chain(self) -> S:
        tag = self.tag()
        if tag is not None:
            return tag
        raise ChainedMethodError("method chaining is unavailable, underlying instance is missing")

    def normalize_attribute(self, attribute: str) -> str:
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

        if (tag := self.tag()) is not None and (normalize := getattr(tag, "normalize_attribute", None)) is not None:
            attribute = normalize(attribute)

        return attribute

    def normalize_pair(self, attribute: str, value: str | bool) -> tuple[str, str | None]:
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
            value = self.attributes[name]
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
                self.classes.replace(normalized)
            return

        if normalized is None:
            self.attributes.pop(name, None)
        else:
            self.attributes[name] = normalized

    def __delitem__(self, key: str, /) -> None:
        name = self.normalize_attribute(key)
        if name == "class":
            self.classes.clear()
        else:
            del self.attributes[name]

    def __iter__(self) -> Iterator[str]:
        if self.classes:
            return itertools.chain(iter(self.attributes), itertools.repeat("class", 1))
        return iter(self.attributes)

    def __len__(self) -> int:
        if self.classes:
            return len(self.attributes) + 1
        return len(self.attributes)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, dict):
            return {**self.attributes, "class": " ".join(self.classes)} == other

        if not isinstance(other, Attributes):
            return NotImplemented

        return self.attributes == other.attributes and self.classes == other.classes

    def render(
        self, flags: RenderFlags = RenderFlags.PRETTY, pretty: bool | None = None, xhtml: bool | None = None
    ) -> str:
        flags = flags.with_arguments(pretty=pretty, xhtml=xhtml)
        stream = RenderStream()
        self._render(stream)
        return stream.getvalue()

    def _render(self, stream: RenderStream) -> None:
        items: Iterable[tuple[str, str]]
        if self.classes:
            items = itertools.chain(self.attributes.items(), (("class", self.classes.render()),))
        else:
            items = self.attributes.items()

        with stream.parts() as parts:
            for name, value in sorted(items):
                self._render_attribute(name, value, parts)

    def _render_attribute(self, name: str, value: str, parts: RenderParts) -> None:
        if name == value and not (parts.flags & RenderFlags.XHTML):
            parts.append(name)
        else:
            parts.append(f'{name}="{value}"')

    def set(self, key: str, value: str | bool) -> S:
        self[key] = value
        return self._chain()

    def delete(self, key: str) -> S:
        del self[key]
        return self._chain()

    def __repr__(self) -> str:
        return f"Attributes({self.render()})"


@dc.dataclass()
class AttributesProperty(Generic[S]):
    name: str | None = dc.field(default=None, init=False)
    attribute: str | None = dc.field(default=None, init=False)

    def __set_name__(self, owner: type[S], name: str) -> None:
        self.name = name
        self.attribute = f"_{self.name}_inner"

    @overload
    def __get__(self, instance: S, owner: type[S] | None = None) -> "Attributes[S]": ...

    @overload
    def __get__(self, instance: None, owner: type[S] | None = None) -> "Self": ...

    def __get__(self, instance: S | None, owner: type[S] | None = None) -> "Attributes[S] | Self":
        if instance is None:
            return self
        assert isinstance(self.attribute, str), "Accessing attributes before __set_name__ was called"
        if (attributes := getattr(instance, self.attribute, None)) is not None:
            return attributes
        attributes = Attributes.from_tag(instance)
        setattr(instance, self.attribute, attributes)
        return attributes

    def classes(self) -> "ClassesProperty":
        return ClassesProperty(weakref.ref(self))


@dc.dataclass()
class ClassesProperty(Generic[S]):
    attributes: weakref.ReferenceType[AttributesProperty[S]]

    @overload
    def __get__(self, instance: S, owner: type[S]) -> "Classes[S]": ...

    @overload
    def __get__(self, instance: None, owner: type[S]) -> "Self": ...

    def __get__(self, instance: S | None, owner: type[S]) -> "Classes[S] | Self":
        if instance is None:
            return self
        attributes = self.attributes()
        if attributes is None:
            raise ValueError("Attributes has been garbage collected")
        return attributes.__get__(instance, owner).classes


class _HasAttributes(Protocol):
    @property
    def attributes(self) -> MutableMapping[str, str | bool]: ...


T = TypeVar("T", bound="dom_tag | _HasAttributes")


@dc.dataclass(frozen=True)
class PrefixAccessor(Generic[T]):
    """A helper for accessing attributes with a prefix."""

    #: Attribute prefix
    prefix: str

    def __get__(self, instance: T, owner: type[T]) -> "PrefixAccess":
        return PrefixAccess(self.prefix, instance)


@dc.dataclass(frozen=True, slots=True)
class PrefixAccess(MutableMapping[str, str | bool], Generic[T]):
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
        """Set an attribute with the given name."""
        self[name] = value
        return self.tag

    def remove(self, name: str) -> T:
        """Remove an attribute with the given name."""
        del self[name]
        return self.tag
