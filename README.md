# BitePlate — Smart Restaurant Management System (SRMS)

**Unit 27: Advanced Programming — Y/615/1651 — Pearson BTEC Level 5 Higher National**

A prototype restaurant management system built in Python to demonstrate
Object-Oriented Programming principles and industry-standard design patterns.
This repository covers **Task 3 (LO3 — Code Implementation)** of the Unit 27
assignment brief.

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
│   └── test_biteplate.py       # Unit tests (unittest)
├── README.md
├── EVALUATION.md               # Task 3c technical evaluation (Distinction)
└── TZ.md                       # Technical specification / requirements
```

---

## How to Run

You need only **Python 3.10+** — no external packages, no database server,
nothing to install.

**1. Run the automated demonstration** (recommended for the first run — it
exercises every feature and pattern in one pass and produces the output used
for the portfolio screenshots):

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

## Data Storage / Persistence — *(read this if you are wondering "which database does it use?")*

**BitePlate does not use any database (no SQLite, MySQL, PostgreSQL, files or
JSON). All data lives in memory while the program runs and is discarded when it
exits.** This is intentional and is exactly what the brief asks for.

| Data | Where it is stored | File |
|------|--------------------|------|
| Tables | `Dict[int, Table]` | `services/restaurant.py` |
| Staff | `Dict[str, Staff]` | `services/restaurant.py` |
| Orders | `Dict[int, Order]` | `services/restaurant.py` |
| Order history | `List[OrderRecord]` inside the Singleton | `patterns/order_history.py` |
| Kitchen queue | `List[Command]` (pending + history) | `patterns/kitchen_queue.py` |

**Why no database is correct here:** Task 3b of the brief specifies the history
log as a **Singleton** —

> *"Implement an OrderHistoryLog class that can only be instantiated once.
> Every confirmed order must be appended to the log with: order ID, table
> number, staff ID, items, total, and timestamp."*

It requires a single in-memory log object, **not** disk persistence. The word
*"persistent"* in the Section 1 scenario describes the conceptual product, and
a real database is discussed only as a **hypothetical scaling question** in
Task 3c (*"if the system scaled to 50 restaurants sharing one central
database…"*) — to be **analysed in `EVALUATION.md`, not implemented**. The
in-memory Singleton therefore fully satisfies the assessable requirement.

---

## Design Patterns Implemented

| Pattern   | Category    | Location                     | Role in BitePlate                                  |
|-----------|-------------|------------------------------|----------------------------------------------------|
| Command   | Behavioural | `patterns/kitchen_queue.py`  | Encapsulates kitchen actions; supports undo        |
| Singleton | Creational  | `patterns/order_history.py`  | One global order-history log                       |
| Strategy  | Behavioural | `patterns/pricing.py`        | Swappable pricing/discount algorithms at runtime   |
| State     | Behavioural | `models/table.py`            | Table lifecycle Free→Reserved→Occupied→AwaitingBill→Cleared |
| Composite | Structural  | `models/menu_item.py`        | Combo meals treated like single items              |
| Decorator | Structural  | `models/order.py`            | Add extras (cheese, allergen flag, side) at runtime|
| Iterator  | Behavioural | `patterns/order_history.py`  | Uniform traversal of history records (`__iter__`)  |
| Facade    | Structural  | `services/restaurant.py`     | Simple interface over complex subsystems           |

### The three required patterns (Command + Strategy + Singleton) working together

The brief requires the three patterns to collaborate in one coherent flow.
In `RestaurantFacade.generate_bill()` they do exactly that:

1. A waiter places an order which is sent to the kitchen as a **Command**
   (`PrepareOrderCommand` on the `KitchenQueue`, with full `undo()` support).
2. The **Strategy** (`PricingContext` + a `PricingStrategy`) calculates the
   discounted total at billing time, swappable at runtime.
3. The confirmed order is appended to the **Singleton** history log
   (`OrderHistoryLog`), which is then traversable via the **Iterator**.

---

## OOP Principles Demonstrated

- **Encapsulation** — private attributes (`_price`, `_items`, `_priced_total`)
  behind read-only `@property` accessors; monetary totals are computed through
  methods and can never be set directly from outside (`Bill.set_priced_total`
  validates input).
- **Inheritance** — `Starter / MainCourse / Dessert / Beverage` extend
  `MenuItem`; `Waiter / Chef / Cashier / Manager` extend `Staff`.
- **Polymorphism** — `get_price()` / `describe()` behave correctly for any item
  type, including combos (`ComboMeal`) and decorated items (`ExtraCheese`,
  `AllergenFlag`, `SideSubstitution`); `can_perform()` answers per role.
- **Abstraction** — `MenuItem`, `Command`, `PricingStrategy`, `TableState` and
  `Staff` are abstract base classes (`abc.ABC`) defining contracts.
- **Generics / containers** — typed `List[OrderItem]`, `List[Command]`,
  `Dict[int, Table]`, `Set[str]` permissions.

### Five UML class relationships present in the code

| Relationship | Example in the code |
|--------------|---------------------|
| Generalisation / Inheritance | `MenuItem → Starter/MainCourse/Dessert/Beverage` |
| Realisation | `PrepareOrderCommand` realises the `Command` interface (ABC) |
| Dependency | `RestaurantFacade` depends on `KitchenQueue`, `PricingContext` |
| Aggregation | `Table` holds a `List[Order]`; `Order` holds `List[OrderItem]` |
| Composition | `Bill` is composed of `BillLineItem`s created and owned by it |

---

## Secure Coding Practices

- All user input is validated (`read_int` rejects non-numbers; menu codes are
  checked before use).
- Constructors raise `ValueError` / `TypeError` on invalid data (negative
  prices, empty names, zero quantity, wrong types).
- The interactive loop catches and reports exceptions instead of crashing.
- No hardcoded credentials or sensitive values anywhere in the codebase.

---

## Screenshots for the Portfolio

The brief requires **at least four screenshots** of the application running.
Run each command, then capture your terminal window.

| # | What to capture | Command to run |
|---|-----------------|----------------|
| 1 | Seating + order taking + Decorator/Composite items (demo sections [1] and [2]) | `python main.py --demo` (top of output) |
| 2 | Kitchen queue Command pattern + undo (demo sections [3] and [3b]) | `python main.py --demo` (middle of output) |
| 3 | Pricing strategies + itemised bill (demo sections [4] and [5]) | `python main.py --demo` (lower output) |
| 4 | All unit tests passing | `python -m unittest tests.test_biteplate -v` |

Optional extra: capture the order history + permissions (demo sections [6] and [7]).

---

## Submission Note

Per the assignment brief, the final portfolio is submitted as a **zipped folder**
via the learning platform. *"Password-protected archives and Google Drive links
will not be accepted."* This GitHub repository is convenient for version control,
but for the official submission, export this folder as a `.zip` (including the
source, `README.md`, `EVALUATION.md`, and your four screenshots) and upload it
to the learning platform as instructed by your tutor.
