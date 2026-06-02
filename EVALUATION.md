# EVALUATION — BitePlate SRMS

This evaluation addresses the trade-offs of the three required patterns, the
limitations of the Singleton implementation, and how the design would change
at scale. (Task 3c — Distinction criterion D3.)

## Were the three patterns the best fit?

**Command (kitchen queue).** The kitchen needs to queue actions, process them
in order, and undo the most recent one when a waiter changes their mind. The
Command pattern fits this exactly because it turns each action into an object
that carries both its `execute()` and its `undo()` logic, plus the state needed
to reverse itself (the previous order status). The alternative considered was a
plain list of status changes with a separate "reverse" function, but that would
scatter the undo logic away from the action it reverses and would not extend
cleanly to new action types such as "expedite". Command keeps each action
self-contained and the invoker (`KitchenQueue`) ignorant of what each command
actually does.

**Singleton (order history).** Every subsystem must write to one shared audit
log, and analytics must read from that same log. A Singleton guarantees a single
shared instance without passing a reference through every constructor. The
alternative was dependency injection — creating one log object in `main` and
passing it everywhere — which is more testable but adds plumbing to every class.
For a single-process prototype the Singleton is the simpler, clearer choice; at
scale the trade-off reverses (see below).

**Strategy (pricing).** Prices must change at runtime based on time of day or
loyalty tier, and new pricing modes must be addable without touching the billing
code. Strategy isolates each algorithm behind one interface so the `Bill` never
changes. The alternative — a single `calculate_total` method with `if/elif`
branches per mode — violates the Open/Closed principle: every new mode edits
existing, tested code. Strategy was clearly the better fit.

## Trade-offs of the Singleton implementation

My Singleton uses `__new__` to return one cached instance. This is simple and
correct in a single-threaded program, but it has two weaknesses. **Testability:**
because the instance persists across the whole process, tests can leak state into
one another; I mitigated this with a `reset()` class method that tests call in
`setUp`, but a true global is still harder to isolate than an injected object.
**Thread safety:** if two kitchen threads called `OrderHistoryLog()` at the exact
same moment, both could pass the `is None` check before either assigned the
instance, creating two logs. A production version would guard `__new__` with a
`threading.Lock` (double-checked locking) or use a module-level instance created
at import time, which Python's import system makes thread-safe.

## Scaling to 50 restaurants on one central database

Several decisions would have to change. The **Singleton** is the biggest: a
single in-memory instance cannot be shared across 50 machines, so the history
log would become a thin client over a shared database, and "one instance" would
mean one connection pool per process rather than one global object. The
**in-memory storage** (Python lists) would move to persistent tables, and the
Iterator would page results from the database instead of walking a list. The
**Strategy** and **Command** patterns would survive almost unchanged, which is
itself evidence that they were well chosen — they encapsulate behaviour, not
storage. Finally, order IDs (currently a process-local counter) would need a
database sequence or UUID to stay unique across branches.
