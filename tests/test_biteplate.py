"""
test_b011biteplate.py
---------------------
Test suite for the BitePlate system. Run with:
    python -m unittest tests.test_biteplate -v
or simply:
    python tests/test_biteplate.py

Covers normal operation, the three required patterns, and edge cases
(empty kitchen queue, illegal table transitions, permission denial,
singleton identity).
"""

import unittest
from datetime import datetime, timedelta

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.menu_item import Starter, MainCourse, Dessert, Beverage, ComboMeal
from models.order import Order, OrderItem, ExtraCheese, AllergenFlag
from models.table import Table
from models.bill import Bill
from models.staff import Waiter, Chef, Cashier, Manager
from patterns.pricing import (StandardPricing, HappyHourPricing,
                              LoyaltyCardPricing, PricingContext)
from patterns.kitchen_queue import (KitchenQueue, PrepareOrderCommand,
                                    CancelOrderCommand)
from patterns.order_history import OrderHistoryLog


class TestMenuItems(unittest.TestCase):
    def test_polymorphic_price_and_category(self):
        items = [Starter("Soup", 3), MainCourse("Steak", 15),
                 Dessert("Pie", 5), Beverage("Cola", 2)]
        cats = [i.get_category() for i in items]
        self.assertEqual(cats, ["Starter", "Main", "Dessert", "Beverage"])
        self.assertEqual(items[1].get_price(), 15)

    def test_negative_price_rejected(self):
        with self.assertRaises(ValueError):
            MainCourse("Bad", -1)

    def test_composite_combo_price(self):
        combo = ComboMeal("Deal", discount=0.10)
        combo.add(MainCourse("Burger", 10)).add(Beverage("Drink", 2))
        self.assertAlmostEqual(combo.get_price(), 10.80)  # (12) * 0.9
        self.assertEqual(combo.get_category(), "Combo")


class TestDecorator(unittest.TestCase):
    def test_extra_cheese_adds_cost(self):
        burger = MainCourse("Burger", 8.0)
        decorated = ExtraCheese(burger)
        self.assertEqual(decorated.get_price(), 9.50)
        self.assertIn("Extra Cheese", decorated.describe())

    def test_allergen_flag_no_cost(self):
        salmon = MainCourse("Salmon", 12.0)
        flagged = AllergenFlag(salmon, "Fish")
        self.assertEqual(flagged.get_price(), 12.0)
        self.assertIn("ALLERGEN", flagged.describe())


class TestOrder(unittest.TestCase):
    def test_subtotal(self):
        o = Order(1, "W01")
        o.add_item(OrderItem(MainCourse("Burger", 8.0), 2))
        self.assertEqual(o.subtotal(), 16.0)

    def test_cannot_add_after_status_change(self):
        o = Order(1, "W01")
        o.set_status(Order.IN_KITCHEN)
        with self.assertRaises(RuntimeError):
            o.add_item(OrderItem(Dessert("Pie", 5), 1))

    def test_invalid_quantity(self):
        with self.assertRaises(ValueError):
            OrderItem(Dessert("Pie", 5), 0)


class TestTableState(unittest.TestCase):
    def test_full_lifecycle(self):
        t = Table(1, 4)
        self.assertEqual(t.state_name, "Free")
        t.seat();          self.assertEqual(t.state_name, "Occupied")
        t.request_bill();  self.assertEqual(t.state_name, "AwaitingBill")
        t.clear();         self.assertEqual(t.state_name, "Cleared")
        t.clear();         self.assertEqual(t.state_name, "Free")

    def test_illegal_transition_raises(self):
        t = Table(1, 4)
        with self.assertRaises(RuntimeError):
            t.request_bill()  # cannot request bill while Free


class TestStrategy(unittest.TestCase):
    def setUp(self):
        self.order = Order(1, "W01")
        self.order.add_item(OrderItem(MainCourse("Burger", 10.0), 1))  # subtotal 10

    def test_standard(self):
        self.assertEqual(StandardPricing().calculate_total(self.order), 10.0)

    def test_happy_hour(self):
        self.assertEqual(HappyHourPricing().calculate_total(self.order), 8.0)

    def test_loyalty(self):
        # 10 * 0.9 = 9.0, minus 2.50 free drink = 6.50
        self.assertEqual(LoyaltyCardPricing().calculate_total(self.order), 6.50)

    def test_runtime_swap(self):
        ctx = PricingContext(StandardPricing())
        self.assertEqual(ctx.price(self.order), 10.0)
        ctx.set_strategy(HappyHourPricing())
        self.assertEqual(ctx.price(self.order), 8.0)


class TestCommand(unittest.TestCase):
    def setUp(self):
        self.chef = Chef("C01", "Bek")
        self.order = Order(1, "W01")
        self.queue = KitchenQueue()

    def test_prepare_and_history(self):
        self.queue.submit(PrepareOrderCommand(self.chef, self.order))
        self.queue.run_next()
        self.assertEqual(self.order.status, Order.PREPARING)
        self.assertEqual(self.queue.history_count(), 1)

    def test_undo_restores_status(self):
        self.queue.submit(CancelOrderCommand(self.chef, self.order))
        self.queue.run_next()
        self.assertEqual(self.order.status, Order.CANCELLED)
        self.queue.undo_last()
        self.assertEqual(self.order.status, Order.PENDING)

    def test_empty_queue_raises(self):
        with self.assertRaises(RuntimeError):
            self.queue.run_next()

    def test_undo_with_no_history_raises(self):
        with self.assertRaises(RuntimeError):
            self.queue.undo_last()


class TestSingleton(unittest.TestCase):
    def setUp(self):
        OrderHistoryLog.reset()

    def test_single_instance(self):
        a = OrderHistoryLog()
        b = OrderHistoryLog()
        self.assertIs(a, b)

    def test_record_and_iterate(self):
        log = OrderHistoryLog()
        log.record(1, 2, "W01", ["Burger", "Burger", "Cola"], 20.0)
        log.record(2, 3, "W01", ["Burger", "Pie"], 15.0)
        self.assertEqual(log.count(), 2)
        # iterator
        ids = [rec.order_id for rec in log]
        self.assertEqual(ids, [1, 2])
        # most frequent
        self.assertEqual(log.most_frequent_item(), "Burger")
        self.assertEqual(log.total_revenue(), 35.0)

    def test_date_range_and_table_filter(self):
        log = OrderHistoryLog()
        now = datetime.now()
        log.record(1, 2, "W01", ["A"], 10.0, timestamp=now - timedelta(days=40))
        log.record(2, 2, "W01", ["B"], 12.0, timestamp=now)
        recent = log.in_date_range(now - timedelta(days=30), now)
        self.assertEqual(len(recent), 1)
        self.assertEqual(len(log.for_table(2)), 2)


class TestPermissions(unittest.TestCase):
    def test_role_capabilities(self):
        self.assertTrue(Cashier("CA1", "D").can_perform("close_bill"))
        self.assertFalse(Cashier("CA1", "D").can_perform("prepare_order"))
        self.assertTrue(Chef("C01", "B").can_perform("reprioritise_queue"))
        self.assertTrue(Manager("M01", "S").can_perform("view_reports"))
        self.assertFalse(Waiter("W01", "A").can_perform("view_reports"))


class TestBill(unittest.TestCase):
    def test_tax_and_total(self):
        o = Order(1, "W01")
        o.add_item(OrderItem(MainCourse("Burger", 10.0), 1))
        bill = Bill(o)  # 12% tax
        self.assertEqual(bill.subtotal(), 10.0)
        self.assertEqual(bill.tax(), 1.20)
        self.assertEqual(bill.total(), 11.20)

    def test_split(self):
        o = Order(1, "W01")
        o.add_item(OrderItem(MainCourse("Burger", 10.0), 1))
        bill = Bill(o)
        self.assertEqual(bill.split(2), 5.60)


if __name__ == "__main__":
    unittest.main(verbosity=2)
