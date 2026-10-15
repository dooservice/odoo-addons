"""The links already used, one empty file each beside the filestore, never in the database.

Created exclusively: two workers that receive the same link at once cannot both take it.
"""

import os
import time
from pathlib import Path

from odoo.tools import config

from ..constants import USED_FOLDER, USED_KEPT_SECONDS
from .token import ConnectRefused


class UsedLinks:
    def __init__(self):
        self.folder = Path(config["data_dir"]) / USED_FOLDER

    def take(self, nonce):
        if not nonce.isalnum():
            raise ConnectRefused("the link's nonce is not one the platform makes")
        self.folder.mkdir(parents=True, exist_ok=True)
        self.forget_old()
        try:
            descriptor = os.open(self.folder / nonce, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as error:
            raise ConnectRefused("the link was used already") from error
        os.close(descriptor)

    def forget_old(self):
        before = time.time() - USED_KEPT_SECONDS
        for used in self.folder.iterdir():
            if used.stat().st_mtime < before:
                used.unlink(missing_ok=True)
