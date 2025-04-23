import dataclasses as dc
from collections.abc import Iterator
from collections.abc import MutableMapping
from collections.abc import MutableSet
from typing import Protocol
from typing import TypeVar
from typing import Generic


class _HasAttributes(Protocol):
    attributes: dict[str, str | bool]


T = TypeVar("T", bound=_HasAttributes)


class Classes(MutableSet[str], Generic[T]):
    """A helper for manipulating the class attribute on a tag."""

    def __init__(self, tag: T) -> None:
        self.tag = tag

    def _classes(self) -> list[str]:
        value = self.tag.attributes.get("class", "")
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value)}")
        return value.split()

    def __contains__(self, cls: object) -> bool:
        return cls in self._classes()

    def __iter__(self) -> Iterator[str]:
        return iter(self._classes())

    def __len__(self) -> int:
        return len(self._classes())

    def add(self, *classes: str) -> T:  # type: ignore[override]
        """Add classes to the tag."""
        current: list[str] = self._classes()
        for cls in classes:
            if cls not in current:
                current.append(cls)
        self.tag.attributes["class"] = " ".join(current)
        return self.tag

    def remove(self, *classes: str) -> T:  # type: ignore[override]
        """Remove classes from the tag."""
        current: list[str] = self._classes()
        for cls in classes:
            if cls in current:
                current.remove(cls)
        self.tag.attributes["class"] = " ".join(current)
        return self.tag

    def discard(self, value: str) -> T:  # type: ignore[override]
        """Remove a class if it exists."""
        self.remove(value)
        return self.tag

    def swap(self, old: str, new: str) -> T:
        """Swap one class for another."""
        current: list[str] = self._classes()
        if old in current:
            current.remove(old)
        if new not in current:
            current.append(new)
        self.tag.attributes["class"] = " ".join(current)
        return self.tag


@dc.dataclass(frozen=True, slots=True)
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
