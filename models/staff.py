"""
staff.py
--------
Staff hierarchy for the BitePlate system.

Demonstrates:
  * Inheritance  -> Waiter, Chef, Cashier, Manager extend Staff.
  * Polymorphism -> can_perform() answers correctly per role.
  * Encapsulation-> staff_id and role permissions are protected.

Permissions are modelled as a set of capability strings. Adding a new role
only requires a new subclass that declares its own permission set - existing
code does not change (Open/Closed principle).
"""

from abc import ABC
from typing import Set


class Staff(ABC):
    """Abstract base class for all staff members."""

    # subclasses override this with their allowed capabilities
    _PERMISSIONS: Set[str] = set()

    def __init__(self, staff_id: str, name: str) -> None:
        if not staff_id or not staff_id.strip():
            raise ValueError("Staff ID cannot be empty.")
        if not name or not name.strip():
            raise ValueError("Staff name cannot be empty.")
        self._staff_id = staff_id.strip()
        self._name = name.strip()

    @property
    def staff_id(self) -> str:
        return self._staff_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def role(self) -> str:
        return self.__class__.__name__

    def can_perform(self, capability: str) -> bool:
        """Polymorphic permission check shared by all roles."""
        return capability in self._PERMISSIONS

    def __str__(self) -> str:
        return f"{self._name} ({self.role}, ID={self._staff_id})"


class Waiter(Staff):
    _PERMISSIONS = {"take_order", "view_kitchen", "serve"}


class Chef(Staff):
    _PERMISSIONS = {"view_kitchen", "prepare_order", "reprioritise_queue"}


class Cashier(Staff):
    _PERMISSIONS = {"view_bill", "close_bill", "take_payment"}


class Manager(Staff):
    # Manager can do everything - union of all capabilities plus admin rights
    _PERMISSIONS = {
        "take_order", "view_kitchen", "serve",
        "prepare_order", "reprioritise_queue",
        "view_bill", "close_bill", "take_payment",
        "view_reports", "manage_staff",
    }
