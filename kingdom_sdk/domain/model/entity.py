from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID

from kingdom_sdk.domain.model.exception import KingdomError
from kingdom_sdk.utils import time


class Entity(ABC):
    """Represent the base element in the domain model, for entities and its
    aggregates.

    Args:
        id: Global unique identifier.
        version: Value used to handle optmistic concurrency.
    """

    _id: UUID
    _version: int
    _is_discarded: bool
    _registered_at: datetime
    _updated_at: datetime

    def __init__(
        self,
        id: UUID,  # noqa
        version: int,
        is_discarded: bool,
        created_at: datetime,
    ):
        self._id = id
        self._version = version
        self._is_discarded = is_discarded
        self._registered_at = created_at
        self._updated_at = created_at

    def _check_not_discarded(self) -> None:
        if self.is_discarded:
            classname = self.__class__.__name__
            raise EntityDiscardedError(f"{classname} object is discarded")

    def _base_representation(self, identifier: str, **kwargs: str) -> str:
        """Use this method in the __repr__ implementation.

        >>> def __repr__(...) -> str:
        ...     return self._base_representation(...)
        """
        pairs = ", ".join([f"{key}={value}" for key, value in kwargs.items()])
        return "{prefix}<{classname} '{identifier}'{extra}>".format(
            prefix="**DISCARDED** " if self.is_discarded else "",
            classname=self.__class__.__name__,
            identifier=identifier,
            extra=f" ({pairs})" if kwargs else "",
        )

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def version(self) -> int:
        return self._version

    @property
    def is_discarded(self) -> bool:
        return self._is_discarded

    def update(self) -> None:
        """Remember to call this method before commiting a change."""
        self._check_not_discarded()
        self._version += 1
        self._updated_at = time.generate_now()


class EntityDiscardedError(KingdomError):
    def __init__(self, message: str):
        super().__init__(message, "ENTITY_DISCARDED_ERROR")
