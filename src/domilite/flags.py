import enum
from typing import Any


class Flag(enum.Flag):
    def __getattr__(self, key: str) -> Any:
        if key.startswith("is_") and key[3:].upper() in type(self).__members__:
            target = type(self).__members__[key[3:].upper()]
            return target in self
        raise AttributeError(key)
