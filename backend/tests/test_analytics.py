from decimal import Decimal

from app import crud
from app.models import Employee


def test_pay_stats_never_mixes_currencies(db_session, make_employee):
    """Regression test for the bug caught during seed-data QA: aggregating
    salary amounts across different currencies produces a meaningless number.
    Each (department, currency) combination must be its own row."""
    make_employee(department="Engineering", currency="USD", salary=Decimal("100000.00"))
    make_employee(department="Engineering", currency="USD", salary=Decimal("120000.00"))
    make_employee(department="Engineering", currency="INR", salary=Decimal("4500000.00"))

    stats = crud.pay_stats_by(db_session, Employee.department)

    engineering_rows = [row for row in stats if row["group"] == "Engineering"]
    assert len(engineering_rows) == 2  # one row per currency, not merged

    usd_row = next(r for r in engineering_rows if r["currency"] == "USD")
    inr_row = next(r for r in engineering_rows if r["currency"] == "INR")

    assert usd_row["headcount"] == 2
    assert usd_row["avg_salary"] == Decimal("110000.00")

    assert inr_row["headcount"] == 1
    assert inr_row["avg_salary"] == Decimal("4500000.00")


def test_median_with_odd_count(db_session, make_employee):
    for amount in ("10000.00", "20000.00", "30000.00"):
        make_employee(department="Sales", currency="USD", salary=Decimal(amount))

    stats = crud.pay_stats_by(db_session, Employee.department)
    row = next(r for r in stats if r["group"] == "Sales")

    assert row["median_salary"] == Decimal("20000.00")


def test_median_with_even_count(db_session, make_employee):
    for amount in ("10000.00", "20000.00", "30000.00", "40000.00"):
        make_employee(department="Marketing", currency="USD", salary=Decimal(amount))

    stats = crud.pay_stats_by(db_session, Employee.department)
    row = next(r for r in stats if r["group"] == "Marketing")

    # median of 20000/30000 = 25000
    assert row["median_salary"] == Decimal("25000.00")


def test_pay_stats_uses_latest_salary_only(client, db_session, make_employee):
    """An employee's earlier salary records must not count toward the
    aggregate once a newer one exists."""
    employee = make_employee(department="Finance", currency="USD", salary=Decimal("50000.00"))
    client.post(
        f"/employees/{employee.id}/salary",
        json={"amount": "70000.00", "currency": "USD", "effective_date": "2025-06-01"},
    )

    stats = crud.pay_stats_by(db_session, Employee.department)
    row = next(r for r in stats if r["group"] == "Finance")

    assert row["headcount"] == 1
    assert row["avg_salary"] == Decimal("70000.00")


def test_analytics_endpoint_rejects_unknown_dimension(client):
    response = client.get("/analytics/pay-by/not_a_real_field")
    assert response.status_code == 400