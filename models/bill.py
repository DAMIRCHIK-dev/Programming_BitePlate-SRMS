"""
bill.py
-------
Bill and BillLineItem.

Demonstrates:
  * Composition -> a Bill is composed of BillLineItems that cannot exist
                   independently of the Bill (they are created inside it and
                   die with it).
  * Encapsulation -> monetary totals are computed through methods, never set
                     directly from outside.
"""

from typing import List

from models.order import Order


class BillLineItem:
    """A single priced line on a bill. Owned entirely by its Bill (composition)."""

    def __init__(self, description: str, amount: float) -> None:
        if not description or not description.strip():
            raise ValueError("Line item description cannot be empty.")
        if amount < 0:
            raise ValueError("Line item amount cannot be negative.")
        self._description = description.strip()
        self._amount = round(float(amount), 2)

    @property
    def description(self) -> str:
        return self._description

    @property
    def amount(self) -> float:
        return self._amount

    def __str__(self) -> str:
        return f"{self._description:<30} {self._amount:>8.2f}"


class Bill:
    """
    An itemised bill for an order.

    The line items are created and held internally (composition). Tax and tip
    are applied through controlled methods so totals can never be tampered with.
    """

    DEFAULT_TAX_RATE = 0.12  # 12% VAT

    def __init__(self, order: Order, tax_rate: float = DEFAULT_TAX_RATE) -> None:
        if not isinstance(order, Order):
            raise TypeError("A Bill must be built from an Order.")
        if not 0.0 <= tax_rate < 1.0:
            raise ValueError("Tax rate must be between 0 and 1.")
        self._order = order
        self._tax_rate = tax_rate
        self._lines: List[BillLineItem] = []
        self._tip = 0.0
        self._priced_total = order.subtotal()  # may be overridden by a strategy

        # build composed line items from the order
        for oi in order.items:
            self._lines.append(BillLineItem(
                f"{oi.quantity}x {oi.item.name}", oi.line_total()
            ))

    @property
    def lines(self) -> List[BillLineItem]:
        return list(self._lines)

    def set_priced_total(self, amount: float) -> None:
        """Used by the pricing strategy to apply a discounted subtotal."""
        if amount < 0:
            raise ValueError("Priced total cannot be negative.")
        self._priced_total = round(float(amount), 2)

    def add_tip(self, tip: float) -> None:
        if tip < 0:
            raise ValueError("Tip cannot be negative.")
        self._tip = round(float(tip), 2)

    def subtotal(self) -> float:
        return round(self._priced_total, 2)

    def tax(self) -> float:
        return round(self._priced_total * self._tax_rate, 2)

    def total(self) -> float:
        return round(self.subtotal() + self.tax() + self._tip, 2)

    def split(self, ways: int) -> float:
        """Split the total evenly between guests."""
        if ways < 1:
            raise ValueError("Cannot split a bill fewer than 1 way.")
        return round(self.total() / ways, 2)

    def render(self) -> str:
        """Return a printable itemised receipt."""
        lines = [f"--- BILL for Order #{self._order.order_id} "
                 f"(Table {self._order.table_number}) ---"]
        for ln in self._lines:
            lines.append(str(ln))
        lines.append("-" * 40)
        lines.append(f"{'Subtotal':<30} {self.subtotal():>8.2f}")
        lines.append(f"{'Tax (' + str(int(self._tax_rate * 100)) + '%)':<30} {self.tax():>8.2f}")
        if self._tip:
            lines.append(f"{'Tip':<30} {self._tip:>8.2f}")
        lines.append(f"{'TOTAL':<30} {self.total():>8.2f}")
        return "\n".join(lines)
