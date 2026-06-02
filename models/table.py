"""
table.py
--------
Table lifecycle modelled with the STATE pattern.

A table moves through: Free -> Reserved -> Occupied -> AwaitingBill -> Cleared.
Each state is its own class that knows which transitions are legal, so the
Table object never holds a tangle of if/else checks - it simply delegates to
its current state object.
"""

from abc import ABC, abstractmethod
from typing import List

from models.order import Order


class TableState(ABC):
    """Abstract state. Each concrete state defines the legal next transitions."""

    name: str = "Undefined"

    @abstractmethod
    def reserve(self, table: "Table") -> None: ...

    @abstractmethod
    def seat(self, table: "Table") -> None: ...

    @abstractmethod
    def request_bill(self, table: "Table") -> None: ...

    @abstractmethod
    def clear(self, table: "Table") -> None: ...

    def _illegal(self, action: str) -> None:
        raise RuntimeError(f"Cannot '{action}' while table is '{self.name}'.")


class FreeState(TableState):
    name = "Free"

    def reserve(self, table): table._set_state(ReservedState())
    def seat(self, table): table._set_state(OccupiedState())
    def request_bill(self, table): self._illegal("request_bill")
    def clear(self, table): self._illegal("clear")


class ReservedState(TableState):
    name = "Reserved"

    def reserve(self, table): self._illegal("reserve")
    def seat(self, table): table._set_state(OccupiedState())
    def request_bill(self, table): self._illegal("request_bill")
    def clear(self, table): table._set_state(FreeState())  # reservation cancelled


class OccupiedState(TableState):
    name = "Occupied"

    def reserve(self, table): self._illegal("reserve")
    def seat(self, table): self._illegal("seat")
    def request_bill(self, table): table._set_state(AwaitingBillState())
    def clear(self, table): self._illegal("clear")


class AwaitingBillState(TableState):
    name = "AwaitingBill"

    def reserve(self, table): self._illegal("reserve")
    def seat(self, table): self._illegal("seat")
    def request_bill(self, table): self._illegal("request_bill")
    def clear(self, table): table._set_state(ClearedState())


class ClearedState(TableState):
    name = "Cleared"

    def reserve(self, table): self._illegal("reserve")
    def seat(self, table): self._illegal("seat")
    def request_bill(self, table): self._illegal("request_bill")
    def clear(self, table): table._set_state(FreeState())  # reset for next guests


class Table:
    """A restaurant table that delegates lifecycle behaviour to its state."""

    def __init__(self, number: int, seats: int) -> None:
        if number < 1:
            raise ValueError("Table number must be positive.")
        if seats < 1:
            raise ValueError("A table must have at least one seat.")
        self._number = number
        self._seats = seats
        self._state: TableState = FreeState()
        self._orders: List[Order] = []   # aggregation: table holds its orders

    @property
    def number(self) -> int:
        return self._number

    @property
    def seats(self) -> int:
        return self._seats

    @property
    def state_name(self) -> str:
        return self._state.name

    @property
    def orders(self) -> List[Order]:
        return list(self._orders)

    def _set_state(self, state: TableState) -> None:
        self._state = state

    # delegated lifecycle actions
    def reserve(self) -> None:
        self._state.reserve(self)

    def seat(self) -> None:
        self._state.seat(self)

    def request_bill(self) -> None:
        self._state.request_bill(self)

    def clear(self) -> None:
        self._state.clear(self)

    def attach_order(self, order: Order) -> None:
        if not isinstance(order, Order):
            raise TypeError("Only Order objects can be attached to a table.")
        self._orders.append(order)

    def __str__(self) -> str:
        return f"Table {self._number} ({self._seats} seats) - {self._state.name}"
