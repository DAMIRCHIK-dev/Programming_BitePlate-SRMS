"""
order.py
--------
Order, OrderItem and meal-customisation Decorators.

Demonstrates:
  * Aggregation -> an Order holds a collection of OrderItems.
  * Composition -> OrderItems cannot meaningfully exist without their Order.
  * Decorator   -> ExtraCheese / AllergenFlag / SideSubstitution wrap a
                   MenuItem to add cost/behaviour at runtime without subclassing.
  * Generics    -> typed List[OrderItem] container.
"""

from typing import List
from datetime import datetime

from models.menu_item import MenuItem


# --------------------------------------------------------------------------
# DECORATOR pattern - dynamically add extras to any MenuItem at runtime
# --------------------------------------------------------------------------
class ItemDecorator(MenuItem):
    """Base decorator. Wraps a MenuItem and forwards/extends its behaviour."""

    def __init__(self, wrapped: MenuItem) -> None:
        if not isinstance(wrapped, MenuItem):
            raise TypeError("A decorator can only wrap a MenuItem.")
        # do NOT call super().__init__ with price; we delegate to the wrapped item
        self._wrapped = wrapped
        self._name = wrapped.name

    def get_category(self) -> str:
        return self._wrapped.get_category()


class ExtraCheese(ItemDecorator):
    EXTRA_COST = 1.50

    def get_price(self) -> float:
        return round(self._wrapped.get_price() + self.EXTRA_COST, 2)

    def describe(self) -> str:
        return f"{self._wrapped.describe()} + Extra Cheese"


class AllergenFlag(ItemDecorator):
    """Marks an item with an allergen note. No cost, but changes the description."""

    def __init__(self, wrapped: MenuItem, allergen: str) -> None:
        super().__init__(wrapped)
        self._allergen = allergen

    def get_price(self) -> float:
        return self._wrapped.get_price()

    def describe(self) -> str:
        return f"{self._wrapped.describe()} [ALLERGEN: {self._allergen}]"


class SideSubstitution(ItemDecorator):
    def __init__(self, wrapped: MenuItem, new_side: str, extra_cost: float = 0.0) -> None:
        super().__init__(wrapped)
        if extra_cost < 0:
            raise ValueError("Substitution cost cannot be negative.")
        self._new_side = new_side
        self._extra_cost = extra_cost

    def get_price(self) -> float:
        return round(self._wrapped.get_price() + self._extra_cost, 2)

    def describe(self) -> str:
        return f"{self._wrapped.describe()} (side: {self._new_side})"


# --------------------------------------------------------------------------
# OrderItem and Order
# --------------------------------------------------------------------------
class OrderItem:
    """A single line in an order: one MenuItem and a quantity."""

    def __init__(self, item: MenuItem, quantity: int = 1) -> None:
        if not isinstance(item, MenuItem):
            raise TypeError("OrderItem requires a MenuItem.")
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
        self._item = item
        self._quantity = quantity

    @property
    def item(self) -> MenuItem:
        return self._item

    @property
    def quantity(self) -> int:
        return self._quantity

    def line_total(self) -> float:
        return round(self._item.get_price() * self._quantity, 2)

    def __str__(self) -> str:
        return f"{self._quantity} x {self._item.describe()} = {self.line_total():.2f}"


class Order:
    """
    An order placed at a table.

    AGGREGATION: holds a collection of OrderItems (the items it aggregates
    are conceptually owned by the order for its lifetime).
    """

    _next_id = 1

    # order lifecycle states (simple State modelling)
    PENDING = "Pending"
    IN_KITCHEN = "InKitchen"
    PREPARING = "Preparing"
    SERVED = "Served"
    CANCELLED = "Cancelled"

    def __init__(self, table_number: int, waiter_id: str) -> None:
        if table_number < 1:
            raise ValueError("Table number must be positive.")
        if not waiter_id or not waiter_id.strip():
            raise ValueError("Waiter ID is required to open an order.")
        self._order_id = Order._next_id
        Order._next_id += 1
        self._table_number = table_number
        self._waiter_id = waiter_id.strip()
        self._items: List[OrderItem] = []
        self._status = Order.PENDING
        self._created_at = datetime.now()

    # --- read-only properties ---
    @property
    def order_id(self) -> int:
        return self._order_id

    @property
    def table_number(self) -> int:
        return self._table_number

    @property
    def waiter_id(self) -> str:
        return self._waiter_id

    @property
    def status(self) -> str:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def items(self) -> List[OrderItem]:
        # return a copy so callers cannot mutate the internal list directly
        return list(self._items)

    # --- behaviour ---
    def add_item(self, order_item: OrderItem) -> None:
        if self._status != Order.PENDING:
            raise RuntimeError(
                f"Cannot modify order #{self._order_id}: status is '{self._status}'."
            )
        if not isinstance(order_item, OrderItem):
            raise TypeError("Only OrderItem objects can be added.")
        self._items.append(order_item)

    def set_status(self, new_status: str) -> None:
        valid = {Order.PENDING, Order.IN_KITCHEN, Order.PREPARING,
                 Order.SERVED, Order.CANCELLED}
        if new_status not in valid:
            raise ValueError(f"Unknown order status: {new_status}")
        self._status = new_status

    def subtotal(self) -> float:
        return round(sum(line.line_total() for line in self._items), 2)

    def __str__(self) -> str:
        return (f"Order #{self._order_id} (Table {self._table_number}, "
                f"{self._status}, {len(self._items)} items, "
                f"subtotal {self.subtotal():.2f})")
