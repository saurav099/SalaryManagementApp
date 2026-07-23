from datetime import date
from decimal import Decimal


def test_list_employees_is_paginated(client, make_employee):
    for i in range(5):
        make_employee(name=f"Employee {i}")

    response = client.get("/employees", params={"page": 1, "page_size": 2})
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 5
    assert len(body["items"]) == 2
    assert body["page"] == 1
    assert body["page_size"] == 2


def test_filter_by_department(client, make_employee):
    make_employee(name="Alice", department="Engineering")
    make_employee(name="Bob", department="Sales")

    response = client.get("/employees", params={"department": "Sales"})
    body = response.json()

    assert body["total"] == 1
    assert body["items"][0]["name"] == "Bob"


def test_search_by_name(client, make_employee):
    make_employee(name="Jane Doe")
    make_employee(name="John Smith")

    response = client.get("/employees", params={"search": "Jane"})
    body = response.json()

    assert body["total"] == 1
    assert body["items"][0]["name"] == "Jane Doe"


def test_get_nonexistent_employee_returns_404(client):
    response = client.get("/employees/99999")
    assert response.status_code == 404


def test_get_employee_detail_includes_salary_history(client, make_employee):
    employee = make_employee(salary=Decimal("80000.00"), effective_date=date(2024, 1, 1))

    response = client.get(f"/employees/{employee.id}")
    body = response.json()

    assert response.status_code == 200
    assert len(body["salary_records"]) == 1
    assert body["salary_records"][0]["amount"] == "80000.00"


def test_salary_update_creates_new_record_not_overwrite(client, make_employee):
    """The core architectural decision: updating salary must ADD a history
    row, never mutate the existing one."""
    employee = make_employee(salary=Decimal("80000.00"), effective_date=date(2024, 1, 1))

    response = client.post(
        f"/employees/{employee.id}/salary",
        json={
            "amount": "95000.00",
            "currency": "USD",
            "effective_date": "2025-01-01",
            "reason": "annual review",
        },
    )
    assert response.status_code == 200

    detail = client.get(f"/employees/{employee.id}").json()
    assert len(detail["salary_records"]) == 2

    amounts = {record["amount"] for record in detail["salary_records"]}
    assert amounts == {"80000.00", "95000.00"}


def test_list_view_shows_most_recent_salary(client, make_employee):
    employee = make_employee(salary=Decimal("80000.00"), effective_date=date(2024, 1, 1))
    client.post(
        f"/employees/{employee.id}/salary",
        json={"amount": "95000.00", "currency": "USD", "effective_date": "2025-01-01"},
    )

    body = client.get("/employees").json()
    item = next(i for i in body["items"] if i["id"] == employee.id)

    assert item["current_salary"]["amount"] == "95000.00"


def test_update_salary_for_nonexistent_employee_returns_404(client):
    response = client.post(
        "/employees/99999/salary",
        json={"amount": "50000.00", "currency": "USD", "effective_date": "2025-01-01"},
    )
    assert response.status_code == 404