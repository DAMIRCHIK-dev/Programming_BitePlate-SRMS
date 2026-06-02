"""
order_history.py
----------------
SINGLETON + ITERATOR patterns for the BitePlate order history log.

OrderHistoryLog guarantees a single global instance shared by every
subsystem. Every confirmed order is appended as an immutable record. The log
provides an iterator so callers can traverse records uniformly regardless of
the internal storage, plus query helpers for analytics.
"""

from datetime import datetime, timedelta
from typing import List, Iterator, Optional, Dict


class OrderRecord:
    """An immutable snapshot of a confirmed order, stored in the history log."""

    def __init__(self, order_id: int, table_number: int, staff_id: str,
                 item_names: List[str], total: float,
                 timestamp: Optional[datetime] = None) -> None:
        self._order_id = order_id
        self._table_number = table_number
        self._staff_id = staff_id
        self._item_names = list(item_names)
        self._total = round(float(total), 2)
        self._timestamp = timestamp or datetime.now()

    @property
    def order_id(self) -> int: return self._order_id
    @property
    def table_number(self) -> int: return self._table_number
    @property
    def staff_id(self) -> str: return self._staff_id
    @property
    def item_names(self) -> List[str]: return list(self._item_names)
    @property
    def total(self) -> float: return self._total
    @property
    def timestamp(self) -> datetime: return self._timestamp

    def __str__(self) -> str:
        ts = self._timestamp.strftime("%Y-%m-%d %H:%M")
        return (f"#{self._order_id} | Table {self._table_number} | "
                f"staff {self._staff_id} | {self._total:.2f} | {ts}")


class OrderHistoryLog:
    """
    SINGLETON. Only one instance can ever exist. The private class attribute
    _instance holds it; __new__ returns the existing instance on every call.
    """

    _instance: Optional["OrderHistoryLog"] = None

    def __new__(cls) -> "OrderHistoryLog":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._records = []   # initialise once
        return cls._instance

    # --- recording ---
    def record(self, order_id: int, table_number: int, staff_id: str,
               item_names: List[str], total: float,
               timestamp: Optional[datetime] = None) -> None:
        rec = OrderRecord(order_id, table_number, staff_id,
                          item_names, total, timestamp)
        self._records.append(rec)

    def count(self) -> int:
        return len(self._records)

    # --- ITERATOR: uniform traversal regardless of storage ---
    def __iter__(self) -> Iterator[OrderRecord]:
        return iter(self._records)

    # --- query helpers for analytics ---
    def in_date_range(self, start: datetime, end: datetime) -> List[OrderRecord]:
        return [r for r in self._records if start <= r.timestamp <= end]

    def for_table(self, table_number: int) -> List[OrderRecord]:
        return [r for r in self._records if r.table_number == table_number]

    def most_frequent_item(self) -> Optional[str]:
        counts: Dict[str, int] = {}
        for rec in self._records:
            for name in rec.item_names:
                counts[name] = counts.get(name, 0) + 1
        if not counts:
            return None
        return max(counts, key=counts.get)

    def total_revenue(self) -> float:
        return round(sum(r.total for r in self._records), 2)

    @classmethod
    def reset(cls) -> None:
        """Test helper: clears the singleton so tests start from a clean state."""
        cls._instance = None
