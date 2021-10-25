from typing import Any, Dict, Tuple

from jinjasql import JinjaSql

from kingdom_sdk.ports.query import (
    AbstractDQLInterface,
    AbstractTemplateSQLMixin,
)
from kingdom_sdk.ports.unit_of_work import AbstractUnitOfWork


class JinjaTemplateSqlMixin(AbstractTemplateSQLMixin):
    _jinja = JinjaSql(param_style="named")

    _sql_file_path: str

    def build_statement(self, **params: Any) -> Tuple[str, Dict]:
        with open(self._sql_file_path) as sql_file:
            file_content = sql_file.read()
        query, bind_params = self._jinja.prepare_query(file_content, params)
        return query, bind_params


class DQLInterface(AbstractDQLInterface, JinjaTemplateSqlMixin):
    def __init__(self, sql_file_path: str) -> None:
        self._sql_file = sql_file_path

    def execute(
        self, uow: AbstractUnitOfWork, commit: bool = False, **params: Any
    ) -> Dict:
        query, bind_params = self.build_statement(**params)
        with uow:
            result = uow.execute_native_sql(query, **bind_params)
            if commit:
                uow.commit()
            return result  # type: ignore
