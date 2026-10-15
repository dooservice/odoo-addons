"""The bot's picture follows the module's icon: the partner was made once and is never rewritten."""

import base64

from odoo import SUPERUSER_ID, api
from odoo.tools.misc import file_open

ICON = "dooservice_brain/static/description/icon.png"
BOT_PARTNER = "dooservice_brain.partner_dooservice"


class BotPicture:
    def __init__(self, cr):
        self.env = api.Environment(cr, SUPERUSER_ID, {})

    def refresh(self):
        bot = self.env.ref(BOT_PARTNER, raise_if_not_found=False)
        if bot:
            with file_open(ICON, "rb") as icon:
                bot.image_1920 = base64.b64encode(icon.read())
            self.env.flush_all()


def migrate(cr, version):
    BotPicture(cr).refresh()
