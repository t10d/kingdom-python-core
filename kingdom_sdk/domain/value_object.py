from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject(ABC):
    """Represent a transient value.

    Implement it as a frozen dataclass.

    >>> from dataclasses import dataclass
    >>> @dataclass(frozen=True)
    ... class MyClass(ValueObject):
    ...     field: type
    """
