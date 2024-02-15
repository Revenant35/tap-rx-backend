from __future__ import annotations


class User:
    user_id: str
    first_name: str
    last_name: str
    phone: str | None
    medications: list[str]
    dependents: list[str]
    monitoring_users: list[str]
    monitored_by_users: list[str]

    def __init__(
            self,
            user_id: str,
            first_name: str,
            last_name: str,
            phone: str | None = None,
            medications: list[str] = None,
            dependents: list[str] = None,
            monitoring_users: list[str] = None,
            monitored_by_users: list[str] = None
    ):
        """
        Initialize a new user object

        Args:
            user_id: {str} The user's ID.
            first_name: {str} The user's first name.
            last_name: {str} The user's last name.
            phone: {str} The user's phone number. Optional.
            medications: {list[str]} The user's medications' UIDS. Optional.
            dependents: {list[str]} The user's dependents' UIDs. Optional.
            monitoring_users: {list[str]} The UIDs of the users this user is monitoring. Optional.
            monitored_by_users: {list[str]} The UIDs of the users monitoring this user. Optional.
        """
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.medications = medications or []
        self.dependents = dependents or []
        self.monitoring_users = monitoring_users or []
        self.monitored_by_users = monitored_by_users or []

    def __repr__(self):
        return f'<{self.__class__.__name__} id=({self.user_id}), name=({self.first_name} {self.last_name})>'

    @staticmethod
    def from_dict(data: dict):
        return User(
            user_id=data["user_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data.get("phone", None),
            medications=data.get("medications", []),
            dependents=data.get("dependents", []),
            monitoring_users=data.get("monitoring_users", []),
            monitored_by_users=data.get("monitored_by_users", [])
        )

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "medications": self.medications,
            "dependents": self.dependents,
            "monitoring_users": self.monitoring_users,
            "monitored_by_users": self.monitored_by_users
        }
