import pytest

from agentsite.query_firewall import QuerySecurityError, TablePolicy, TenantQueryFirewall, TenantQueryPolicy


def firewall():
    return TenantQueryFirewall(TenantQueryPolicy({"products": TablePolicy("products", frozenset({"name", "price", "stock"}))}, max_limit=50))


def test_tenant_predicate_is_added_from_trusted_context():
    query = firewall().compile("SELECT name, price FROM products WHERE price < :max_price LIMIT 500", {"max_price": 1000}, tenant_id="company_a")
    assert "tenant_id = :__tenant_id" in query.sql
    assert "LIMIT 50" in query.sql
    assert query.parameters["__tenant_id"] == "company_a"


def test_tenant_id_cannot_be_supplied_by_model():
    with pytest.raises(QuerySecurityError):
        firewall().compile("SELECT name FROM products WHERE tenant_id = :tenant", {"tenant": "company_b"}, tenant_id="company_a")


def test_unknown_tables_columns_and_writes_are_rejected():
    for sql in ("SELECT secret FROM products", "SELECT name FROM customers", "DELETE FROM products", "SELECT name FROM products; SELECT name FROM products"):
        with pytest.raises(QuerySecurityError):
            firewall().compile(sql, {}, tenant_id="company_a")
