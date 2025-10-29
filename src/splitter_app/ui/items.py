"""Custom table items."""

from PySide6.QtWidgets import QTableWidgetItem


class NumericItem(QTableWidgetItem):
    """QTableWidgetItem that sorts numerically using an internal float value."""

    def __init__(self, text: str, value: float) -> None:
        """NumericItem constructor."""
        super().__init__(text)
        self._num = float(value)

    def numeric_value(self) -> float:
        """Return the internal numeric value."""
        return self._num

    def __lt__(self, other: object) -> bool:
        """Sort by numeric value."""
        if isinstance(other, NumericItem):
            return self._num < other._num
        return super().__lt__(other)


class MoneyItem(NumericItem):
    """Money display like $12.34 / -$12.34 but sorts by the numeric value."""

    def __init__(self, value: float) -> None:
        """MoneyItem constructor."""
        text = f"-${abs(value):.2f}" if value < 0 else f"${value:.2f}"
        super().__init__(text, value)


class GroupBalanceItem(MoneyItem):
    """Custom balance sorter for group summary.

    Ascending sort will behave like numeric ascending.
    Descending sort requested behavior is: positives (desc), 0,
    negatives (asc by magnitude).
    This is achieved naturally when using numeric sort and
    setting descending order in the view.
    """

    # Inherit MoneyItem; keep same comparator (numeric) and formatting.
    # The view's descending sort gives the requested order.
