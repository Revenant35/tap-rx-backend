from __future__ import annotations

default_minute = "0"
default_hour = "0"
default_day_of_month = "*"
default_month = "*"
default_day_of_week = "*"


class Schedule:
    minute: str
    hour: str
    day_of_month: str
    month: str
    day_of_week: str

    def __init__(
            self,
            minute: str = default_minute,
            hour: str = default_hour,
            day_of_month: str = default_day_of_month,
            month: str = default_month,
            day_of_week: str = default_day_of_week,
    ):
        """
        Initialize a new medication object

        Args:
            minute: {str} The minute the medication is scheduled.
            hour: {str} The hour the medication is scheduled.
            day_of_month: {str} The day of the month the medication is scheduled.
            month: {str} The month the medication is scheduled.
            day_of_week: {str} The day of the week the medication is scheduled.
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

        schedule_fields = ["minute", "hour", "day_of_month", "month", "day_of_week"]
        if not any(field in data for field in schedule_fields):
            return None

        return Schedule(
            minute=data.get("minute", default_minute),
            hour=data.get("hour", default_hour),
            day_of_month=data.get("day_of_month", default_day_of_month),
            month=data.get("month", default_month),
            day_of_week=data.get("day_of_week", default_day_of_week)
        )

    def to_dict(self):
        schedule_fields = ["minute", "hour", "day_of_month", "month", "day_of_week"]
        return {field: getattr(self, field) for field in schedule_fields}

    def to_cron(self) -> str:
        return f'{self.minute} {self.hour} {self.day_of_month} {self.month} {self.day_of_week}'
