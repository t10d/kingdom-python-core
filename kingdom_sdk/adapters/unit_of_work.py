from abc import ABC
from typing import Any, Generator, List, Set, Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from kingdom_sdk import config
from kingdom_sdk.domain.aggregate import Aggregate
from kingdom_sdk.ports.unit_of_work import AbstractUnitOfWork

DEFAULT_SESSION_FACTORY = sessionmaker(
    # ISOLATION LEVEL ENSURES aggregate's version IS RESPECTED
    # That is, if version differs it will raise an exception
    bind=create_engine(
        config.get_database_url(),
        isolation_level="REPEATABLE_READ",
    ),
    autoflush=False,
)


class BaseUnitOfWork(AbstractUnitOfWork, ABC):
    """Generic Unit of Work.

    You only need to extend it and annotate the repositories with the full
    import path.

    >>> class MyUnitOfWork(BaseUnitOfWork):
    ...     repository: ...
    """

    _errors: List[Any]
    _session_factory: sessionmaker
    _session: Session

    def __init__(
        self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY
    ) -> None:
        self._errors = []
        self._session_factory = session_factory

    def __enter__(self) -> AbstractUnitOfWork:
        self._session = self._session_factory()
        self._initilize_fields(self._session)
        return super().__enter__()

    def __exit__(self, *args: Any) -> None:
        super().__exit__(*args)
        self._session.close()

    def _commit(self) -> None:
        self._session.commit()

    def _rollback(self) -> None:
        self._session.rollback()

    def collect_new_events(self) -> Generator:
        dirty: Set[Aggregate] = set()

        for field_name, _ in self._repositories:
            field = self.__dict__[field_name]
            if hasattr(field, "_seen"):
                dirty = dirty.union(field._seen)  # noqa

        for aggregate in dirty:
            while aggregate.has_events:
                yield aggregate.next_event

    def _initilize_fields(self, session: Session) -> None:
        for field_name, repository in self._repositories:
            self.__dict__[field_name] = repository(session)

    @property
    def _repositories(self) -> Generator[Tuple[str, Any], Any, None]:
        return (
            (field, module)
            for field, module in self.__annotations__.items()
            if not field.startswith("_")
        )
