from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Protocol


class QuerySecurityError(ValueError):
    """Raised when a model-generated query cannot be proven safe."""


class QueryConnection(Protocol):
    def execute(self, query: str, parameters: dict[str, Any]) -> Any: ...


@dataclass(frozen=True)
class TablePolicy:
    name: str
    columns: frozenset[str]
    tenant_column: str = "tenant_id"


@dataclass(frozen=True)
class TenantQueryPolicy:
    tables: dict[str, TablePolicy]
    max_limit: int = 100


@dataclass(frozen=True)
class SafeQuery:
    sql: str
    parameters: dict[str, Any]
    table: str


class TenantQueryFirewall:
    """Compile a deliberately small, read-only SQL subset into a tenant query.

    This first implementation supports one table and simple SELECT statements.
    Complex SQL is rejected until an AST parser and equivalent security tests are
    added. Database-native row-level security should still be enabled in production.
    """

    _statement = re.compile(
        r"^SELECT\s+(?P<columns>[a-zA-Z0-9_, *]+)\s+FROM\s+(?P<table>[a-zA-Z_][a-zA-Z0-9_]*)"
        r"(?:\s+WHERE\s+(?P<where>.+?))?"
        r"(?:\s+ORDER\s+BY\s+(?P<order>[a-zA-Z_][a-zA-Z0-9_]*)(?:\s+(?P<direction>ASC|DESC))?)?"
        r"(?:\s+LIMIT\s+(?P<limit>[0-9]+))?\s*$",
        re.IGNORECASE,
    )
    _condition = re.compile(
        r"^(?P<column>[a-zA-Z_][a-zA-Z0-9_]*)\s*(?P<operator>=|<=|>=|<|>|LIKE)\s*:(?P<parameter>[a-zA-Z_][a-zA-Z0-9_]*)$",
        re.IGNORECASE,
    )

    def __init__(self, policy: TenantQueryPolicy) -> None:
        self.policy = policy

    def compile(self, sql: str, parameters: dict[str, Any], *, tenant_id: str) -> SafeQuery:
        normalized = sql.strip()
        if not normalized or ";" in normalized or "--" in normalized or "/*" in normalized:
            raise QuerySecurityError("only one clean SELECT statement is allowed")
        if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|EXEC)\b", normalized, re.I):
            raise QuerySecurityError("write and administrative statements are not allowed")
        match = self._statement.fullmatch(normalized)
        if not match:
            raise QuerySecurityError("query is outside the supported safe SELECT subset")
        table_name = match.group("table")
        table = self.policy.tables.get(table_name)
        if table is None:
            raise QuerySecurityError(f"table is not approved: {table_name}")
        columns = [item.strip() for item in match.group("columns").split(",")]
        if "*" in columns:
            raise QuerySecurityError("select * is not allowed")
        if not columns or any(not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", item) or item not in table.columns for item in columns):
            raise QuerySecurityError("query contains an unapproved column")
        where = match.group("where")
        if where and re.search(rf"\b{re.escape(table.tenant_column)}\b", where, re.I):
            raise QuerySecurityError("tenant scope must come from trusted context")
        if where:
            conditions = [part.strip() for part in re.split(r"\s+AND\s+", where, flags=re.I)]
            parsed = [self._condition.fullmatch(condition) for condition in conditions]
            if not all(parsed):
                raise QuerySecurityError("WHERE may contain only parameterized AND conditions")
            used = {item.group("parameter") for item in parsed}
            missing = used - parameters.keys()
            if missing:
                raise QuerySecurityError(f"missing query parameters: {', '.join(sorted(missing))}")
        order = match.group("order")
        if order and order not in table.columns:
            raise QuerySecurityError("ORDER BY column is not approved")
        requested_limit = int(match.group("limit") or self.policy.max_limit)
        if requested_limit < 1:
            raise QuerySecurityError("LIMIT must be positive")
        limit = min(requested_limit, self.policy.max_limit)
        safe_parameters = dict(parameters)
        safe_parameters["__tenant_id"] = tenant_id
        safe_sql = f"SELECT {', '.join(columns)} FROM {table.name}"
        safe_sql += f" WHERE ({where}) AND {table.tenant_column} = :__tenant_id" if where else f" WHERE {table.tenant_column} = :__tenant_id"
        if order:
            safe_sql += f" ORDER BY {order} {match.group('direction') or 'ASC'}"
        safe_sql += f" LIMIT {limit}"
        return SafeQuery(safe_sql, safe_parameters, table.name)

    def execute(self, connection: QueryConnection, sql: str, parameters: dict[str, Any], *, tenant_id: str) -> Any:
        safe = self.compile(sql, parameters, tenant_id=tenant_id)
        return connection.execute(safe.sql, safe.parameters)
