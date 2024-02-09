from __future__ import annotations


class User:
    user_id: str
    first_name: str
    last_name: str
    phone: str | None
    dependents: list[User]
    guardians: list[User]

    def __init__(self, user_id: str, first_name: str, last_name: str, phone: str | None = None, dependents: list[User] = None, guardians: list[User] = None):
        """
        Initialize a new user object

        Args:
            user_id: {str} The user's ID.
            first_name: {str} The user's first name.
            last_name: {str} The user's last name.
            phone: {str} The user's phone number. Optional.
            dependents: {list[User]} The user's dependents. Optional.
            guardians: {list[User]} The user's guardians. Optional.
        """
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.dependents = dependents if dependents else []
        self.guardians = guardians if guardians else []

    def __repr__(self):
        return f'<{self.__class__.__name__} id=({self.user_id}), name=({self.first_name} {self.last_name})>'

    @staticmethod
    def from_dict(data: dict):
        return User(
            user_id=data["user_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data.get("phone", None),
            dependents=[User.from_dict(dependent) for dependent in data.get("dependents", [])],
            guardians=[User.from_dict(guardian) for guardian in data.get("guardians", [])]
        )

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "dependents": [dependent.to_dict() for dependent in self.dependents],
            "guardians": [guardian.to_dict() for guardian in self.guardians]
        }
