"""
pricing.py
----------
STRATEGY pattern for the BitePlate pricing / discount engine.

A PricingStrategy can be swapped at runtime without changing the Bill class.
Three concrete strategies are provided:
  * StandardPricing    - no discount.
  * HappyHourPricing   - 20% off the whole order.
  * LoyaltyCardPricing  - 10% off plus a free drink credit.

Adding a new strategy (e.g. a weekend surcharge) means writing one new class
that implements calculate_total() - existing code is untouched.
"""

from abc import ABC, abstractmethod

from models.order import Order


class PricingStrategy(ABC):
    """Strategy interface: every strategy turns an order into a final subtotal."""

    @abstractmethod
    def calculate_total(self, order: Order) -> float:
        raise NotImplementedError

    @abstractmethod
    def label(self) -> str:
        raise NotImplementedError


class StandardPricing(PricingStrategy):
    def calculate_total(self, order: Order) -> float:
        return order.subtotal()

    def label(self) -> str:
        return "Standard Pricing"


class HappyHourPricing(PricingStrategy):
    """20% off everything."""

    DISCOUNT = 0.20

    def calculate_total(self, order: Order) -> float:
        return round(order.subtotal() * (1.0 - self.DISCOUNT), 2)

    def label(self) -> str:
        return "Happy Hour (-20%)"


class LoyaltyCardPricing(PricingStrategy):
    """10% off, and one free drink credit (a fixed amount deducted)."""

    DISCOUNT = 0.10
    FREE_DRINK_CREDIT = 2.50

    def calculate_total(self, order: Order) -> float:
        discounted = order.subtotal() * (1.0 - self.DISCOUNT)
        final = max(0.0, discounted - self.FREE_DRINK_CREDIT)
        return round(final, 2)

    def label(self) -> str:
        return "Loyalty Card (-10% + free drink)"


class PricingContext:
    """
    The context that uses a strategy. The billing system holds a
    PricingContext and can swap the strategy at runtime.
    """

    def __init__(self, strategy: PricingStrategy = None) -> None:
        self._strategy = strategy or StandardPricing()

    def set_strategy(self, strategy: PricingStrategy) -> None:
        if not isinstance(strategy, PricingStrategy):
            raise TypeError("Strategy must implement PricingStrategy.")
        self._strategy = strategy

    @property
    def strategy_label(self) -> str:
        return self._strategy.label()

    def price(self, order: Order) -> float:
        return self._strategy.calculate_total(order)
