from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from multimodal.invoice_schema import InvoiceData, InvoiceItem


def test_valid_invoice():
    invoice = InvoiceData(
        invoice_number="INV-001",
        invoice_date=date(2026, 3, 14),
        vendor_name="Brightwater Supplies Ltd",
        total_due=Decimal("21122.00"),
    )

    assert invoice.invoice_number == "INV-001"
    assert invoice.total_due == Decimal("21122.00")


def test_invoice_with_missing_optional_fields():
    invoice = InvoiceData(
        invoice_number="INV-002",
    )

    assert invoice.vendor_name is None
    assert invoice.due_date is None
    assert invoice.items == []


def test_valid_invoice_item():
    item = InvoiceItem(
        description="Office chairs",
        quantity=4,
        unit_price=3200,
        amount=12800,
    )

    assert item.description == "Office chairs"
    assert item.quantity == Decimal(4)
    assert item.amount == Decimal(12800)


def test_empty_item_description_is_invalid():
    with pytest.raises(ValidationError):
        InvoiceItem(description="")


def test_extra_invoice_field_is_rejected():
    with pytest.raises(ValidationError):
        InvoiceData(
            invoice_number="INV-001",
            unknown_field="unexpected",
        )
