from __future__ import annotations

from src.models.Schedule import Schedule


class Medication:
    medication_id: str
    user_id: str
    dependent_id: str | None
    container_id: str | None
    name: str
    nickname: str | None
    dosage: str | None
    schedule: Schedule | None

    def __init__(
            self,
            medication_id: str,
            user_id: str,
            name: str,
            dependent_id: str | None = None,
            container_id: str | None = None,
            nickname: str | None = None,
            dosage: str | None = None,
            schedule: Schedule | None = None
    ):
        """
        Initialize a new medication object

        Args:
            medication_id: {str} The medication's ID.
            user_id: {str} The user's ID.
            name: {str} The medication's name.
            dependent_id: {str} The dependent's ID. Optional.
            container_id: {str} The container's ID. Optional.
            nickname: {str} The medication's nickname. Optional.
            dosage: {str} The medication's dosage. Optional.
            schedule: {Schedule} The medication's schedule. Optional.
        """
        self.medication_id = medication_id
        self.user_id = user_id
        self.name = name
        self.dependent_id = dependent_id
        self.container_id = container_id
        self.nickname = nickname
        self.dosage = dosage
        self.schedule = schedule

    def __eq__(self, other):
        return all(getattr(self, attr) == getattr(other, attr) for attr in vars(self))

    def __repr__(self):
        return f'<{self.__class__.__name__} id=({self.medication_id}), name = ({self.name})>'

    @staticmethod
    def from_dict(data: dict):
        return Medication(
            medication_id=data["medication_id"],
            user_id=data["user_id"],
            name=data["name"],
            dependent_id=data.get("dependent_id", None),
            container_id=data.get("container_id", None),
            nickname=data.get("nickname", None),
            dosage=data.get("dosage", None),
            schedule=Schedule.from_dict(data.get("schedule", None))
        )

    def to_dict(self):
        data = {
            "medication_id": self.medication_id,
            "user_id": self.user_id,
            "name": self.name,
        }

        for attr_name in ["dependent_id", "container_id", "nickname", "dosage"]:
            attr_value = getattr(self, attr_name, None)
            if attr_value is not None:
                data[attr_name] = attr_value

        if self.schedule is not None:
            data["schedule"] = self.schedule.to_dict()

        return data
