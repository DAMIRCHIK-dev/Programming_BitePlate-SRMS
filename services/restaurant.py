"""
restaurant.py
-------------
FACADE for the BitePlate system.

The RestaurantFacade exposes a small, simple interface over the more complex
subsystems (tables, orders, kitchen queue, pricing strategy, history log,
billing). The console UI talks only to this facade, never to the internals.
"""

from typing import Dict, List

from models.table import Table
from models.order import Order, OrderItem
from models.menu_item import MenuItem
from models.staff import Staff, Chef
from models.bill import Bill
from patterns.kitchen_queue import KitchenQueue, PrepareOrderCommand, CancelOrderCommand
from patterns.order_history import OrderHistoryLog
from patterns.pricing import PricingContext, PricingStrategy, StandardPricing


class RestaurantFacade:
    def __init__(self) -> None:
        self._tables: Dict[int, Table] = {}
        self._staff: Dict[str, Staff] = {}
        self._orders: Dict[int, Order] = {}
        self._kitchen = KitchenQueue()
        self._history = OrderHistoryLog()
        self._pricing = PricingContext(StandardPricing())

    # --- setup ---
    def add_table(self, number: int, seats: int) -> Table:
        if number in self._tables:
            raise ValueError(f"Table {number} already exists.")
        table = Table(number, seats)
        self._tables[number] = table
        return table

    def add_staff(self, member: Staff) -> None:
        if member.staff_id in self._staff:
            raise ValueError(f"Staff ID {member.staff_id} already exists.")
        self._staff[member.staff_id] = member

    def get_table(self, number: int) -> Table:
        if number not in self._tables:
            raise KeyError(f"No table numbered {number}.")
        return self._tables[number]

    def get_staff(self, staff_id: str) -> Staff:
        if staff_id not in self._staff:
            raise KeyError(f"No staff with ID {staff_id}.")
        return self._staff[staff_id]

    def list_tables(self) -> List[Table]:
        return list(self._tables.values())

    # --- seating ---
    def seat_customer(self, table_number: int) -> None:
        self.get_table(table_number).seat()

    # --- ordering ---
    def open_order(self, table_number: int, waiter_id: str) -> Order:
        table = self.get_table(table_number)
        waiter = self.get_staff(waiter_id)
        if not waiter.can_perform("take_order"):
            raise PermissionError(f"{waiter.name} is not allowed to take orders.")
        order = Order(table_number, waiter_id)
        self._orders[order.order_id] = order
        table.attach_order(order)
        return order

    def add_to_order(self, order_id: int, item: MenuItem, quantity: int = 1) -> None:
        order = self._get_order(order_id)
        order.add_item(OrderItem(item, quantity))

    def _get_order(self, order_id: int) -> Order:
        if order_id not in self._orders:
            raise KeyError(f"No order #{order_id}.")
        return self._orders[order_id]

    # --- kitchen (Command) ---
    def send_to_kitchen(self, order_id: int, chef_id: str) -> None:
        order = self._get_order(order_id)
        chef = self.get_staff(chef_id)
        if not isinstance(chef, Chef):
            raise PermissionError("Only a Chef can receive kitchen commands.")
        order.set_status(Order.IN_KITCHEN)
        self._kitchen.submit(PrepareOrderCommand(chef, order))

    def cancel_in_kitchen(self, order_id: int, chef_id: str) -> None:
        order = self._get_order(order_id)
        chef = self.get_staff(chef_id)
        if not isinstance(chef, Chef):
            raise PermissionError("Only a Chef can cancel kitchen orders.")
        self._kitchen.submit(CancelOrderCommand(chef, order))

    def process_kitchen(self) -> List[str]:
        return self._kitchen.run_all()

    def undo_last_kitchen_action(self) -> str:
        return self._kitchen.undo_last()

    def view_kitchen_queue(self) -> List[str]:
        return self._kitchen.view_pending()

    # --- pricing (Strategy) ---
    def set_pricing_strategy(self, strategy: PricingStrategy) -> None:
        self._pricing.set_strategy(strategy)

    @property
    def pricing_label(self) -> str:
        return self._pricing.strategy_label

    # --- billing (Facade over Bill + Strategy + Singleton history) ---
    def generate_bill(self, order_id: int, tip: float = 0.0,
                      split_ways: int = 1) -> Bill:
        order = self._get_order(order_id)
        bill = Bill(order)
        # apply the current pricing strategy
        priced = self._pricing.price(order)
        bill.set_priced_total(priced)
        if tip:
            bill.add_tip(tip)

        # record the confirmed order in the singleton history log
        item_names = [oi.item.name for oi in order.items for _ in range(oi.quantity)]
        self._history.record(
            order_id=order.order_id,
            table_number=order.table_number,
            staff_id=order.waiter_id,
            item_names=item_names,
            total=bill.total(),
        )
        return bill

    # --- history (Singleton + Iterator) ---
    @property
    def history(self) -> OrderHistoryLog:
        return self._history
