from datetime import datetime


class MedicationEvent:
    medication_event_id: str
    user_id: str
    medication_id: str
    timestamp: datetime
    dosage: str | None

    def __init__(self, medication_event_id: str, user_id: str, medication_id: str, timestamp: datetime, dosage: str | None = None):
        """
        Initialize a new medication event object

        Args:
            medication_event_id: {str} The medication event's ID.
            user_id: {str} The user's ID.
            medication_id: {str} The medication's ID.
            timestamp: {datetime} The event's timestamp.
            dosage: {str} The event's dosage.
        """
        self.medication_event_id = medication_event_id
        self.user_id = user_id
        self.medication_id = medication_id
        self.timestamp = timestamp
        self.dosage = dosage

    def __eq__(self, other):
        return all(getattr(self, attr) == getattr(other, attr) for attr in vars(self))

    def __repr__(self):
        return f'<{self.__class__.__name__} medication_id=({self.medication_id}) timestamp=({self.timestamp}), dosage=({self.dosage})>'

    @staticmethod
    def from_dict(data: dict):
        return MedicationEvent(
            medication_event_id=data["medication_event_id"],
            user_id=data["user_id"],
            medication_id=data["medication_id"],
            timestamp=data["timestamp"],
            dosage=data.get("dosage", None)
        )

    def to_dict(self):
        return {
            "medication_event_id": self.medication_event_id,
            "user_id": self.user_id,
            "medication_id": self.medication_id,
            "timestamp": self.timestamp.isoformat(),
            "dosage": self.dosage
        }
