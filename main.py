"""
main.py
-------
BitePlate - Smart Restaurant Management System
Console entry point.

Run an automated demonstration of all features and patterns with:
    python main.py --demo

Run the interactive console menu with:
    python main.py

All three required patterns work together in the flow:
    waiter places order (-> Command into kitchen)
    -> pricing strategy calculates the discounted total (Strategy)
    -> the confirmed order is written to the history log (Singleton)
"""

import sys

from services.restaurant import RestaurantFacade
from models.menu_item import Starter, MainCourse, Dessert, Beverage, ComboMeal
from models.order import ExtraCheese, AllergenFlag
from models.staff import Waiter, Chef, Cashier, Manager
from patterns.pricing import StandardPricing, HappyHourPricing, LoyaltyCardPricing


# --------------------------------------------------------------------------
# Shared sample data setup
# --------------------------------------------------------------------------
def build_restaurant() -> RestaurantFacade:
    r = RestaurantFacade()

    # tables
    for num, seats in [(1, 2), (2, 4), (3, 6)]:
        r.add_table(num, seats)

    # staff
    r.add_staff(Waiter("W01", "Aziz"))
    r.add_staff(Chef("C01", "Bek"))
    r.add_staff(Cashier("CA1", "Dilnoza"))
    r.add_staff(Manager("M01", "Sardor"))

    return r


def sample_menu():
    """Return a small menu dictionary keyed by a short code."""
    return {
        "1": Starter("Garlic Bread", 3.50),
        "2": MainCourse("Cheeseburger", 8.90),
        "3": MainCourse("Grilled Salmon", 12.50),
        "4": Dessert("Cheesecake", 4.75),
        "5": Beverage("Fresh Lemonade", 2.50),
    }


# --------------------------------------------------------------------------
# Automated demonstration (used for screenshots / verification)
# --------------------------------------------------------------------------
def run_demo() -> None:
    print("=" * 60)
    print("  BitePlate SRMS - Automated Demonstration")
    print("=" * 60)

    r = build_restaurant()
    menu = sample_menu()

    # 1) Seat a customer
    print("\n[1] SEATING")
    print("   ", r.get_table(2))
    r.seat_customer(2)
    print("    -> seated:", r.get_table(2))

    # 2) Open an order and add items (incl. a Decorator and a Composite combo)
    print("\n[2] TAKING ORDER (Waiter W01 at Table 2)")
    order = r.open_order(2, "W01")
    r.add_to_order(order.order_id, menu["2"], 2)          # 2 cheeseburgers
    r.add_to_order(order.order_id, ExtraCheese(menu["2"]))  # Decorator: +cheese
    r.add_to_order(order.order_id, AllergenFlag(menu["3"], "Fish"))  # allergen
    combo = ComboMeal("Lunch Deal", discount=0.10).add(menu["1"]).add(menu["5"])
    r.add_to_order(order.order_id, combo)                  # Composite combo
    for oi in order.items:
        print("    -", oi)
    print(f"    Subtotal: {order.subtotal():.2f}")

    # 3) Send to kitchen (Command pattern)
    print("\n[3] KITCHEN QUEUE (Command pattern)")
    r.send_to_kitchen(order.order_id, "C01")
    print("    Pending:", r.view_kitchen_queue())
    print("    Processing ->", r.process_kitchen())
    print(f"    Order status now: {order.status}")

    # demonstrate undo
    print("\n[3b] UNDO DEMO")
    order2 = r.open_order(2, "W01")
    r.add_to_order(order2.order_id, menu["4"], 1)
    r.cancel_in_kitchen(order2.order_id, "C01")
    r.process_kitchen()
    print(f"    Order #{order2.order_id} status: {order2.status}")
    print("   ", r.undo_last_kitchen_action())
    print(f"    Order #{order2.order_id} status after undo: {order2.status}")

    # 4) Pricing strategies (Strategy pattern)
    print("\n[4] PRICING STRATEGIES (Strategy pattern)")
    for strat in (StandardPricing(), HappyHourPricing(), LoyaltyCardPricing()):
        r.set_pricing_strategy(strat)
        print(f"    {r.pricing_label:<34} -> total subtotal "
              f"{r._pricing.price(order):.2f}")

    # 5) Generate a bill (Facade + Strategy + Singleton recording)
    print("\n[5] BILLING (Facade)")
    r.set_pricing_strategy(HappyHourPricing())
    bill = r.generate_bill(order.order_id, tip=2.00)
    print("    Strategy applied:", r.pricing_label)
    print()
    for line in bill.render().splitlines():
        print("    " + line)
    print(f"\n    Split 2 ways: {bill.split(2):.2f} each")

    # 6) Order history (Singleton + Iterator)
    print("\n[6] ORDER HISTORY (Singleton + Iterator)")
    print(f"    Records in log: {r.history.count()}")
    for rec in r.history:
        print("    -", rec)
    print(f"    Most frequent item: {r.history.most_frequent_item()}")
    print(f"    Total revenue logged: {r.history.total_revenue():.2f}")

    # 7) Permission check (role-based access)
    print("\n[7] STAFF PERMISSIONS (role-based)")
    cashier = r.get_staff("CA1")
    manager = r.get_staff("M01")
    print(f"    {cashier.name} (Cashier) can close bill? "
          f"{cashier.can_perform('close_bill')}")
    print(f"    {cashier.name} (Cashier) can prepare order? "
          f"{cashier.can_perform('prepare_order')}")
    print(f"    {manager.name} (Manager) can view reports? "
          f"{manager.can_perform('view_reports')}")

    print("\n" + "=" * 60)
    print("  Demonstration complete - all patterns exercised.")
    print("=" * 60)


# --------------------------------------------------------------------------
# Interactive console menu
# --------------------------------------------------------------------------
def read_int(prompt: str) -> int:
    """Safely read an integer from the user."""
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("    ! Please enter a whole number.")


def run_interactive() -> None:
    r = build_restaurant()
    menu = sample_menu()
    current_order = None

    actions = """
BitePlate SRMS - Main Menu
  1. View tables
  2. Seat customer at a table
  3. Open an order (waiter W01)
  4. Add item to current order
  5. View menu
  6. Send current order to kitchen (Chef C01)
  7. Process kitchen queue
  8. Undo last kitchen action
  9. Choose pricing strategy
 10. Generate bill for current order
 11. View order history
  0. Exit
"""
    while True:
        print(actions)
        choice = input("Select an option: ").strip()

        try:
            if choice == "0":
                print("Goodbye!")
                break

            elif choice == "1":
                for t in r.list_tables():
                    print("   ", t)

            elif choice == "2":
                num = read_int("    Table number to seat: ")
                r.seat_customer(num)
                print("    Seated:", r.get_table(num))

            elif choice == "3":
                num = read_int("    Table number for order: ")
                current_order = r.open_order(num, "W01")
                print(f"    Opened {current_order}")

            elif choice == "4":
                if current_order is None:
                    print("    ! Open an order first (option 3).")
                    continue
                print("    Menu codes:", ", ".join(menu.keys()))
                code = input("    Item code: ").strip()
                if code not in menu:
                    print("    ! Unknown item code.")
                    continue
                qty = read_int("    Quantity: ")
                r.add_to_order(current_order.order_id, menu[code], qty)
                print(f"    Added. Subtotal now {current_order.subtotal():.2f}")

            elif choice == "5":
                for code, item in menu.items():
                    print(f"    {code}. {item.describe()}")

            elif choice == "6":
                if current_order is None:
                    print("    ! No current order.")
                    continue
                r.send_to_kitchen(current_order.order_id, "C01")
                print("    Sent to kitchen. Queue:", r.view_kitchen_queue())

            elif choice == "7":
                results = r.process_kitchen()
                if results:
                    for res in results:
                        print("    Processed:", res)
                else:
                    print("    Kitchen queue empty.")

            elif choice == "8":
                print("   ", r.undo_last_kitchen_action())

            elif choice == "9":
                print("    1. Standard  2. Happy Hour  3. Loyalty Card")
                sc = input("    Choose: ").strip()
                strat = {"1": StandardPricing(), "2": HappyHourPricing(),
                         "3": LoyaltyCardPricing()}.get(sc)
                if strat is None:
                    print("    ! Invalid choice.")
                    continue
                r.set_pricing_strategy(strat)
                print("    Pricing set to:", r.pricing_label)

            elif choice == "10":
                if current_order is None:
                    print("    ! No current order.")
                    continue
                tip_raw = input("    Tip amount (0 for none): ").strip()
                try:
                    tip = float(tip_raw) if tip_raw else 0.0
                except ValueError:
                    print("    ! Invalid tip; using 0.")
                    tip = 0.0
                bill = r.generate_bill(current_order.order_id, tip=tip)
                print()
                print(bill.render())

            elif choice == "11":
                print(f"    Records: {r.history.count()}")
                for rec in r.history:
                    print("    -", rec)
                top = r.history.most_frequent_item()
                if top:
                    print("    Most frequent item:", top)

            else:
                print("    ! Unknown option.")

        except (ValueError, KeyError, RuntimeError, PermissionError, TypeError) as exc:
            print(f"    ! Error: {exc}")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
    else:
        run_interactive()


if __name__ == "__main__":
    main()
