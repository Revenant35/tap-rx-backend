from __future__ import annotations


class Dependant:
    dependant_id: str
    first_name: str
    last_name: str
    phone: str | None

    def __init__(
        self,
        dependant_id: str,
        first_name: str,
        last_name: str,
        phone: str | None = None,
    ):
        """
        Initialize a new dependant object

        Args:
            dependant_id: {str} The dependant's unique identifier.
            first_name: {str} The dependant's first name.
            last_name: {str} The dependant's last name.
            phone: {str} The dependant's phone number. Optional.
        """
        self.dependant_id = dependant_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone

    def __eq__(self, other):
        return all(getattr(self, attr) == getattr(other, attr) for attr in vars(self))

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.dependant_id}>"

    @staticmethod
    def from_dict(data: dict):
        return Dependant(
            dependant_id=data["dependant_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data.get("phone", None),
        )

    def to_dict(self):
        return {
            "dependant_id": self.dependant_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
        }
