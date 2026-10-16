"""What the platform says of this project, hours and reviewed processes, asked once every few minutes per database."""

import time

from ..constants import STATUS_KEPT_SECONDS


class StatusCache:
    kept = {}

    @classmethod
    def of(cls, dbname, client):
        stamp, status = cls.kept.get(dbname, (0.0, None))
        if status is None or time.monotonic() - stamp > STATUS_KEPT_SECONDS:
            status = client.status()
            cls.kept[dbname] = (time.monotonic(), status)
        return status

    @classmethod
    def forget(cls, dbname):
        cls.kept.pop(dbname, None)
