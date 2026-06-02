# BitePlate — Smart Restaurant Management System (SRMS)

**Unit 27: Advanced Programming — Y/615/1651 — BTEC Level 5**

A prototype restaurant management system built in Python to demonstrate
Object-Oriented Programming principles and industry-standard design patterns.

---

## Language & IDE Justification

This prototype is written in **Python 3.12** and developed in **Visual Studio
Code**. Python was chosen because its clean, readable syntax lets the design
patterns themselves remain the focus of the code rather than boilerplate. It
has first-class support for object orientation (classes, ABCs, properties,
inheritance) and for the abstractions every pattern in this assignment needs:
the `abc` module expresses the `Command`, `PricingStrategy`, `MenuItem` and
`TableState` interfaces cleanly, `__new__` gives a textbook Singleton, and
`__iter__` provides a native Iterator. VS Code was chosen for its integrated
debugger, built-in terminal, and excellent Python and PlantUML extensions,
which made testing and diagramming fast during development.

---

## Project Structure

```
BitePlate/
├── main.py                     # Console entry point (interactive + --demo)
├── models/
│   ├── menu_item.py            # MenuItem hierarchy + Composite combo
│   ├── order.py                # Order, OrderItem + Decorator customisation
│   ├── table.py                # Table lifecycle (State pattern)
│   ├── staff.py                # Staff roles + permissions
│   └── bill.py                 # Bill, BillLineItem (composition)
├── patterns/
│   ├── pricing.py              # STRATEGY pattern (pricing engine)
│   ├── kitchen_queue.py        # COMMAND pattern (kitchen queue + undo)
│   └── order_history.py        # SINGLETON + ITERATOR (history log)
├── services/
│   └── restaurant.py           # FACADE over all subsystems
├── tests/
│   └── test_biteplate.py       # 24 unit tests
├── README.md
└── EVALUATION.md
```

---

## How to Run

You need only Python 3.10+ (no external packages required).

**1. Run the automated demonstration** (recommended for first run — exercises
every feature and pattern in one pass):

```bash
python main.py --demo
```

**2. Run the interactive console menu:**

```bash
python main.py
```

**3. Run the test suite:**

```bash
python -m unittest tests.test_biteplate -v
```

---

## Design Patterns Implemented

| Pattern   | Category    | Location                     | Role in BitePlate                                  |
|-----------|-------------|------------------------------|----------------------------------------------------|
| Command   | Behavioural | `patterns/kitchen_queue.py`  | Encapsulates kitchen actions; supports undo        |
| Singleton | Creational  | `patterns/order_history.py`  | One global order-history log                       |
| Strategy  | Behavioural | `patterns/pricing.py`        | Swappable pricing/discount algorithms at runtime   |
| State     | Behavioural | `models/table.py`            | Table lifecycle Free→Reserved→…→Cleared            |
| Composite | Structural  | `models/menu_item.py`        | Combo meals treated like single items              |
| Decorator | Structural  | `models/order.py`            | Add extras (cheese, allergen flag) at runtime      |
| Iterator  | Behavioural | `patterns/order_history.py`  | Uniform traversal of history records               |
| Facade    | Structural  | `services/restaurant.py`     | Simple interface over complex subsystems           |

The three **required** patterns (Command, Singleton, Strategy) work together
in one flow: a waiter places an order which is sent to the kitchen as a
**Command**, the **Strategy** calculates the discounted total at billing time,
and the confirmed order is written to the **Singleton** history log.

---

## OOP Principles Demonstrated

- **Encapsulation** — private attributes (`_price`, `_items`) behind read-only properties; totals computed through methods.
- **Inheritance** — `Starter/MainCourse/Dessert/Beverage` extend `MenuItem`; staff roles extend `Staff`.
- **Polymorphism** — `get_price()` / `describe()` behave correctly for any item type, including combos and decorated items.
- **Abstraction** — `MenuItem`, `Command`, `PricingStrategy`, `TableState` are abstract base classes defining contracts.
- **Generics / containers** — typed `List[OrderItem]`, `List[Command]`, `Dict[int, Table]`.

---

## Secure Coding Practices

- All user input is validated (`read_int` rejects non-numbers; menu codes checked).
- Constructors raise `ValueError` / `TypeError` on invalid data (negative prices, empty names, zero quantity).
- The interactive loop catches and reports exceptions instead of crashing.
- No hardcoded credentials or sensitive values anywhere in the codebase.

---

## Screenshots for the Portfolio

Take the four required screenshots from the terminal output as follows. Run
each command, then capture your terminal window.

| # | What to capture | Command to run |
|---|-----------------|----------------|
| 1 | Seating + order taking + Decorator/Composite items (demo sections [1] and [2]) | `python main.py --demo` (top of output) |
| 2 | Kitchen queue Command pattern + undo (demo sections [3] and [3b]) | `python main.py --demo` (middle of output) |
| 3 | Pricing strategies + itemised bill (demo sections [4] and [5]) | `python main.py --demo` (lower output) |
| 4 | All 24 tests passing | `python -m unittest tests.test_biteplate -v` |

Optional extra: capture the order history + permissions (demo sections [6] and [7]).
