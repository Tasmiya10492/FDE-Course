from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InvoiceItem(BaseModel):
    """Represents one item or service on an invoice."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    description: str = Field(min_length=1)
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    amount: Decimal | None = None


class InvoiceData(BaseModel):
    """Represents the complete extracted invoice."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    invoice_number: str | None = None
    invoice_date: date | None = None
    due_date: date | None = None

    vendor_name: str | None = None
    vendor_address: str | None = None
    customer_name: str | None = None

    items: list[InvoiceItem] = Field(default_factory=list)

    currency: str | None = None
    subtotal: Decimal | None = None
    tax_rate: Decimal | None = None
    tax_amount: Decimal | None = None
    total_due: Decimal | None = None

    payment_method: str | None = None
    payment_reference: str | None = None
