"""
kitchen_queue.py
----------------
COMMAND pattern for the BitePlate kitchen action queue.

Each kitchen action is encapsulated as a command object with execute() and
undo(). The KitchenQueue (invoker) stores a history of executed commands and
can undo the most recent one. The Chef is the receiver that actually does the
work.

Concrete commands:
  * PrepareOrderCommand - moves an order into preparation.
  * CancelOrderCommand  - cancels an order (remembers previous status for undo).
"""

from abc import ABC, abstractmethod
from typing import List

from models.order import Order
from models.staff import Chef


class Command(ABC):
    """Command interface: every kitchen action supports execute and undo."""

    @abstractmethod
    def execute(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def undo(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError


class PrepareOrderCommand(Command):
    """Receiver = Chef. Moves an order to 'Preparing'."""

    def __init__(self, chef: Chef, order: Order) -> None:
        if not isinstance(chef, Chef):
            raise TypeError("PrepareOrderCommand requires a Chef receiver.")
        self._chef = chef
        self._order = order
        self._previous_status = None

    def execute(self) -> None:
        self._previous_status = self._order.status
        self._order.set_status(Order.PREPARING)

    def undo(self) -> None:
        if self._previous_status is not None:
            self._order.set_status(self._previous_status)

    def description(self) -> str:
        return (f"Prepare Order #{self._order.order_id} "
                f"(chef {self._chef.name})")


class CancelOrderCommand(Command):
    """Cancels an order, remembering its previous status so it can be undone."""

    def __init__(self, chef: Chef, order: Order) -> None:
        if not isinstance(chef, Chef):
            raise TypeError("CancelOrderCommand requires a Chef receiver.")
        self._chef = chef
        self._order = order
        self._previous_status = None

    def execute(self) -> None:
        self._previous_status = self._order.status
        self._order.set_status(Order.CANCELLED)

    def undo(self) -> None:
        if self._previous_status is not None:
            self._order.set_status(self._previous_status)

    def description(self) -> str:
        return (f"Cancel Order #{self._order.order_id} "
                f"(chef {self._chef.name})")


class KitchenQueue:
    """
    INVOKER. Holds the queue of pending commands and a history of executed
    ones. Supports running the next command, running all, and undoing the
    last executed command.
    """

    def __init__(self) -> None:
        self._pending: List[Command] = []
        self._history: List[Command] = []

    def submit(self, command: Command) -> None:
        if not isinstance(command, Command):
            raise TypeError("Only Command objects can be submitted.")
        self._pending.append(command)

    def run_next(self) -> str:
        if not self._pending:
            raise RuntimeError("Kitchen queue is empty - nothing to run.")
        command = self._pending.pop(0)
        command.execute()
        self._history.append(command)
        return command.description()

    def run_all(self) -> List[str]:
        results = []
        while self._pending:
            results.append(self.run_next())
        return results

    def undo_last(self) -> str:
        if not self._history:
            raise RuntimeError("No executed command to undo.")
        command = self._history.pop()
        command.undo()
        return f"Undone: {command.description()}"

    def pending_count(self) -> int:
        return len(self._pending)

    def history_count(self) -> int:
        return len(self._history)

    def view_pending(self) -> List[str]:
        return [c.description() for c in self._pending]
