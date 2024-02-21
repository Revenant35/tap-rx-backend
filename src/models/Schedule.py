from __future__ import annotations


class Schedule:
    minute: str | None
    hour: str | None
    day_of_month: str | None
    month: str | None
    day_of_week: str | None

    def __init__(
            self,
            minute: str | None = None,
            hour: str | None = None,
            day_of_month: str | None = None,
            month: str | None = None,
            day_of_week: str | None = None
    ):
        """
        Initialize a new medication object

        Args:
            minute: {str} The minute the medication is scheduled. Optional.
            hour: {str} The hour the medication is scheduled. Optional.
            day_of_month: {str} The day of the month the medication is scheduled. Optional.
            month: {str} The month the medication is scheduled. Optional.
            day_of_week: {str} The day of the week the medication is scheduled. Optional.
        """
        self.minute = minute
        self.hour = hour
        self.day_of_month = day_of_month
        self.month = month
        self.day_of_week = day_of_week

    def __eq__(self, other):
        return all(getattr(self, attr) == getattr(other, attr) for attr in vars(self))

    @staticmethod
    def from_dict(data: dict):
        if not data:
            return None

        return Schedule(
            minute=data.get("minute", None),
            hour=data.get("hour", None),
            day_of_month=data.get("day_of_month", None),
            month=data.get("month", None),
            day_of_week=data.get("day_of_week", None)
        )

    def to_dict(self):
        schedule_fields = ["minute", "hour", "day_of_month", "month", "day_of_week"]
        return {field: getattr(self, field, None) for field in schedule_fields if getattr(self, field, None) is not None}
