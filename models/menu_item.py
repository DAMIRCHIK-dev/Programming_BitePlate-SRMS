"""
menu_item.py
------------
Defines the MenuItem hierarchy for the BitePlate system.

Demonstrates:
  * Abstraction   -> MenuItem is an abstract base class (ABC).
  * Inheritance   -> Starter, MainCourse, Dessert, Beverage extend MenuItem.
  * Polymorphism  -> get_price() / describe() behave correctly for any subtype.
  * Composite     -> ComboMeal treats individual dishes and bundles uniformly.
"""

from abc import ABC, abstractmethod
from typing import List


class MenuItem(ABC):
    """Abstract base class. Every concrete menu item must define a category."""

    def __init__(self, name: str, price: float) -> None:
        if not name or not name.strip():
            raise ValueError("Menu item name cannot be empty.")
        if price < 0:
            raise ValueError("Menu item price cannot be negative.")
        self._name = name.strip()      # encapsulated (private by convention)
        self._price = float(price)

    # --- public read-only access (encapsulation) ---
    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def get_price(self) -> float:
        """Return the price of this item. Overridden by every subclass/composite."""
        raise NotImplementedError

    @abstractmethod
    def get_category(self) -> str:
        """Return the kitchen routing category (Starter, Main, etc.)."""
        raise NotImplementedError

    def describe(self) -> str:
        """Polymorphic description used uniformly across all item types."""
        return f"{self._name} ({self.get_category()}) - {self.get_price():.2f}"


class Starter(MenuItem):
    def get_price(self) -> float:
        return self._price

    def get_category(self) -> str:
        return "Starter"


class MainCourse(MenuItem):
    def get_price(self) -> float:
        return self._price

    def get_category(self) -> str:
        return "Main"


class Dessert(MenuItem):
    def get_price(self) -> float:
        return self._price

    def get_category(self) -> str:
        return "Dessert"


class Beverage(MenuItem):
    def get_price(self) -> float:
        return self._price

    def get_category(self) -> str:
        return "Beverage"


class ComboMeal(MenuItem):
    """
    COMPOSITE pattern participant.

    A ComboMeal is itself a MenuItem but is composed of several child
    MenuItems. The client can call get_price() / describe() on an individual
    dish or a whole combo in exactly the same way - they are treated uniformly.
    """

    def __init__(self, name: str, discount: float = 0.0) -> None:
        # combos start at price 0; the price is the sum of their children
        super().__init__(name, 0.0)
        if not 0.0 <= discount < 1.0:
            raise ValueError("Combo discount must be between 0 and 1 (e.g. 0.10).")
        self._discount = discount
        self._items: List[MenuItem] = []

    def add(self, item: MenuItem) -> "ComboMeal":
        if not isinstance(item, MenuItem):
            raise TypeError("Only MenuItem objects can be added to a combo.")
        self._items.append(item)
        return self  # allow chaining

    def get_price(self) -> float:
        total = sum(child.get_price() for child in self._items)
        return round(total * (1.0 - self._discount), 2)

    def get_category(self) -> str:
        return "Combo"

    def describe(self) -> str:
        contents = ", ".join(child.name for child in self._items)
        saving = f" ({int(self._discount * 100)}% off)" if self._discount else ""
        return f"{self._name} [Combo: {contents}]{saving} - {self.get_price():.2f}"
