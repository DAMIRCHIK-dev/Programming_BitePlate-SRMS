# Technical Specification (TZ) — BitePlate SRMS

**Project:** BitePlate — Smart Restaurant Management System (SRMS)
**Unit:** Pearson BTEC Level 5 — Unit 27: Advanced Programming (Y/615/1651)
**Scope of this document:** Task 3 (LO3) — the working code prototype
**Language / Runtime:** Python 3.10+ (standard library only)
**Document status:** Implemented and verified against the unit tests

---

## 1. Purpose

This document defines the technical requirements for the BitePlate SRMS
prototype and records how each requirement is satisfied in the source code. It
serves as the bridge between the assignment brief (the *what*) and the
implementation in this repository (the *how*).

The system models the core operations of a restaurant — seating, ordering,
kitchen preparation, pricing, billing and order history — using
Object-Oriented Programming and a set of classic design patterns.

---

## 2. Scope

### 2.1 In scope (implemented)

- Table lifecycle management (State pattern).
- Order taking with item customisation and combo meals.
- Kitchen queue with execute / undo (Command pattern).
- Runtime-swappable pricing and discounts (Strategy pattern).
- Itemised billing with tax, tip and split (composition).
- Single global order-history log with traversal and analytics
  (Singleton + Iterator).
- Role-based staff permissions.
- A console UI (interactive menu + automated `--demo`).

### 2.2 Out of scope (not required by Task 3)

- Persistent storage / database (data is in-memory only — see §7).
- Graphical user interface (a console UI is permitted by the brief).
- Networking, multi-user concurrency, authentication.
- The reservation reminder pipeline and multi-station kitchen routing
  (these appear in Task 4 as *design* scenarios, not Task 3 code).

---

## 3. Definitions

| Term | Meaning |
|------|---------|
| SRMS | Smart Restaurant Management System |
| Facade | Single entry-point object (`RestaurantFacade`) the UI talks to |
| Receiver | The object a Command acts upon (the `Chef`) |
| Invoker | The object that triggers Commands (the `KitchenQueue`) |
| Strategy | An interchangeable pricing algorithm |
| Singleton | A class with exactly one instance (`OrderHistoryLog`) |

---

## 4. Functional Requirements

Each requirement is traceable to the brief and to the file that implements it.

| ID | Requirement | Implemented in | Brief ref |
|----|-------------|----------------|-----------|
| FR-1 | A table moves through Free → Reserved → Occupied → AwaitingBill → Cleared, rejecting illegal transitions | `models/table.py` (State pattern) | §1, 3a |
| FR-2 | A waiter can open an order at a table and add multiple items | `services/restaurant.py`, `models/order.py` | 3a |
| FR-3 | Menu items support customisation (extra cheese, allergen flag, side substitution) added at runtime | `models/order.py` (Decorator) | §1, 3a |
| FR-4 | Combo / set meals are priced and displayed like a single item | `models/menu_item.py` (`ComboMeal`, Composite) | §1, 3a |
| FR-5 | Orders are sent to the kitchen as commands; the last action can be undone | `patterns/kitchen_queue.py` (Command) | 3b-1 |
| FR-6 | Two concrete commands exist: prepare and cancel, each with `execute()` and `undo()` | `patterns/kitchen_queue.py` | 3b-1 |
| FR-7 | Exactly one order-history log exists; every confirmed order is appended with order ID, table, staff ID, items, total, timestamp | `patterns/order_history.py` (Singleton) | 3b-2 |
| FR-8 | The history can be queried by date range, by table, and for the most frequent item, and traversed via an iterator | `patterns/order_history.py` (Iterator) | 3b-2 |
| FR-9 | A `PricingStrategy` interface with `calculate_total(order)` and at least three strategies: Standard, HappyHour (-20%), Loyalty (-10% + free drink) | `patterns/pricing.py` (Strategy) | 3b-3 |
| FR-10 | Pricing strategy can be swapped at runtime without changing the `Bill` class | `patterns/pricing.py`, `models/bill.py` | 3b-3 |
| FR-11 | An itemised bill is generated with tax, optional tip, and even split between guests | `models/bill.py` (composition) | §1, 3a |
| FR-12 | Staff roles (Waiter, Chef, Cashier, Manager) have distinct permissions checked via `can_perform()` | `models/staff.py` | §1 |
| FR-13 | The three required patterns (Command, Strategy, Singleton) collaborate in one flow | `RestaurantFacade.generate_bill()` | 3b |
| FR-14 | A console UI lets a user seat a customer, place an order, view the kitchen queue and generate a bill | `main.py` | 3a |

---

## 5. Non-Functional Requirements

| ID | Requirement | How it is met |
|----|-------------|---------------|
| NFR-1 Security | All external input validated; no crashes on bad input | `read_int()` loop, menu-code checks, try/except in the interactive loop |
| NFR-2 Robustness | Invalid object state is impossible to construct | Constructors raise `ValueError` / `TypeError` (negative price, empty name, zero quantity, wrong type) |
| NFR-3 No secrets | No hardcoded credentials or sensitive values | None present in the codebase |
| NFR-4 Portability | Runs anywhere with Python 3.10+ | Standard library only; no third-party packages |
| NFR-5 Maintainability | New roles / strategies / commands added without modifying existing code | Open/Closed via ABCs and Strategy/Command/State subclassing |
| NFR-6 Testability | Behaviour verified automatically | `tests/test_biteplate.py` (`python -m unittest`) |
| NFR-7 Encapsulation | Monetary totals cannot be tampered with | Private fields behind read-only properties; totals via methods |

---

## 6. System Architecture

The console UI (`main.py`) talks **only** to a single Facade
(`RestaurantFacade`), which orchestrates the subsystems. No UI code reaches
into the internals.

```
        ┌──────────────┐
        │   main.py    │  console UI (interactive + --demo)
        └──────┬───────┘
               │ calls
        ┌──────▼────────────┐
        │ RestaurantFacade  │  services/restaurant.py
        └──┬───┬───┬───┬────┘
           │   │   │   │
   ┌───────┘   │   │   └────────────┐
   ▼           ▼   ▼                ▼
 Tables     Orders  KitchenQueue   OrderHistoryLog
 (State)  (Decorator/  (Command)    (Singleton +
          Composite)                 Iterator)
                       │
                       ▼
                 PricingContext (Strategy) ──▶ Bill (composition)
```

### 6.1 Module responsibilities

| Module | Responsibility |
|--------|----------------|
| `models/menu_item.py` | Menu hierarchy + Composite combo |
| `models/order.py` | Order, OrderItem, Decorator customisations |
| `models/table.py` | Table lifecycle via the State pattern |
| `models/staff.py` | Staff hierarchy + permission sets |
| `models/bill.py` | Bill + BillLineItem, tax/tip/split |
| `patterns/kitchen_queue.py` | Command interface, concrete commands, invoker |
| `patterns/order_history.py` | Singleton log + Iterator + analytics |
| `patterns/pricing.py` | Strategy interface, concrete strategies, context |
| `services/restaurant.py` | Facade orchestrating all of the above |

---

## 7. Data Model & Storage

**Storage type: in-memory only. No database, no files.**

All state is held in standard Python containers for the lifetime of the
process and discarded on exit:

| Entity | Container | Owner |
|--------|-----------|-------|
| Table | `Dict[int, Table]` | `RestaurantFacade` |
| Staff | `Dict[str, Staff]` | `RestaurantFacade` |
| Order | `Dict[int, Order]` | `RestaurantFacade` |
| OrderItem | `List[OrderItem]` | `Order` (aggregation) |
| OrderRecord | `List[OrderRecord]` | `OrderHistoryLog` (Singleton) |
| Command | `List[Command]` (pending + history) | `KitchenQueue` |
| BillLineItem | `List[BillLineItem]` | `Bill` (composition) |

**Rationale.** Task 3b specifies the history as a *Singleton* object, not as
durable storage. A real database is only a hypothetical scaling question in
Task 3c, to be discussed in `EVALUATION.md`. Adding persistence later would be
localised: the `OrderHistoryLog.record()` / `__iter__` methods are the single
seam where a repository (e.g. SQLite) could be introduced without touching the
rest of the system.

---

## 8. Design Pattern Specification

| Pattern | Participants (in this code) | Intent satisfied |
|---------|-----------------------------|------------------|
| Command | `Command` (interface), `PrepareOrderCommand`, `CancelOrderCommand`, `KitchenQueue` (invoker), `Chef` (receiver) | Encapsulate kitchen actions; queue and undo them |
| Singleton | `OrderHistoryLog` via `__new__` | Exactly one global audit log |
| Strategy | `PricingStrategy`, `StandardPricing`, `HappyHourPricing`, `LoyaltyCardPricing`, `PricingContext` | Swap pricing at runtime without touching `Bill` |
| State | `TableState`, `Free/Reserved/Occupied/AwaitingBill/Cleared` | Lifecycle transitions without if/else tangle |
| Composite | `MenuItem`, `ComboMeal` | Treat single dishes and bundles uniformly |
| Decorator | `ItemDecorator`, `ExtraCheese`, `AllergenFlag`, `SideSubstitution` | Add cost/behaviour to items at runtime |
| Iterator | `OrderHistoryLog.__iter__` | Traverse records regardless of internal storage |
| Facade | `RestaurantFacade` | One simple interface over all subsystems |

---

## 9. Constraints & Assumptions

- Single-process, single-user console application.
- IDs (`Order._next_id`) are process-local counters, not globally unique.
- Tax rate is a fixed 12% VAT (`Bill.DEFAULT_TAX_RATE`), configurable per Bill.
- The Singleton is module/process scoped and **not thread-safe** — acceptable
  for a single-threaded console prototype (analysed further in `EVALUATION.md`).

---

## 10. Acceptance Criteria

The prototype is considered to meet this specification when:

1. `python main.py --demo` runs end-to-end and exercises every pattern.
2. `python main.py` provides a working interactive menu for seating, ordering,
   viewing the kitchen queue and generating a bill.
3. `python -m unittest tests.test_biteplate -v` reports **all tests passing**.
4. All requirements FR-1…FR-14 and NFR-1…NFR-7 above are demonstrable.
5. The four portfolio screenshots (see `README.md`) can be reproduced.

---

## 11. Traceability Summary

- **LO3 / 3a (Pass):** FR-1, FR-2, FR-3, FR-4, FR-11, FR-14, NFR-1, NFR-2, NFR-3.
- **LO3 / 3b (Merit):** FR-5…FR-10, FR-12, FR-13.
- **LO3 / 3c (Distinction):** delivered in `EVALUATION.md` (pattern fit,
  Singleton trade-offs, 50-restaurant scaling).
