"""A ticket as the platform describes it, turned into what this Odoo keeps of it."""

from datetime import datetime, timezone

from ..constants import CHANGE_STAGES, TICKET_KINDS, TICKET_STATES, WAITING_FOR


class RemoteValues:
    kinds = dict(TICKET_KINDS)
    states = dict(TICKET_STATES)
    stages = dict(CHANGE_STAGES)
    waiting = dict(WAITING_FOR)

    @classmethod
    def of(cls, remote):
        """What changes while a ticket lives: its kind is only taken when it is opened."""
        return {
            "remote_number": int(remote.get("number") or 0),
            "state": cls.known(cls.states, remote.get("state"), "open"),
            "change_stage": cls.known(cls.stages, remote.get("change_stage"), False),
            "title": remote.get("title") or False,
            "process_name": remote.get("process_name") or False,
            "deadline": cls.when(remote.get("deadline_at")),
            "waiting_for": cls.known(cls.waiting, remote.get("waiting_for"), False),
        }

    @classmethod
    def opened(cls, remote, kind):
        return {**cls.of(remote), "kind": cls.known(cls.kinds, remote.get("kind"), kind)}

    @staticmethod
    def known(options, value, fallback):
        return value if value in options else fallback

    @staticmethod
    def when(value):
        """An ISO instant from the platform, as the naive UTC datetime Odoo stores."""
        if not value:
            return False
        try:
            moment = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return False
        if moment.tzinfo is not None:
            moment = moment.astimezone(timezone.utc).replace(tzinfo=None)
        return moment

    @staticmethod
    def since(value):
        """A stored datetime, as the ISO instant the platform filters by."""
        return value.replace(tzinfo=timezone.utc).isoformat() if value else ""
