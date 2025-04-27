import copy
import enum
from enum import auto
from typing import Any
from typing import Self

__all__ = ["auto", "Flag"]


class Flag(enum.Flag):
    """
    A base-class for flags with two extensions: `is_...` methods
    and :meth:`with_arguments`
    """

    def __getattr__(self, key: str) -> Any:
        if key.startswith("is_") and key[3:].upper() in type(self).__members__:
            target = type(self).__members__[key[3:].upper()]
            return target in self
        raise AttributeError(key)

    def with_arguments(self, **kwargs: bool | None) -> Self:
        """Returns a copy of this flag, having applied the arguments
        supplied as keywords.

        Keywords should be (case-insenstive) names of flag attributes,
        and their values should be booleans (which will force the returned
        flag to have that value) or `None` (which will be ignored)."""
        output = copy.copy(self)
        for key, value in kwargs.items():
            target = type(self)[key.upper()]
            if value is True:
                output |= target
            elif value is False:
                output &= ~target
            elif value is None:
                pass
            else:  # pragma: no cover
                raise TypeError(f"Unexpected argument value for flag: {value!r}")
        return output
