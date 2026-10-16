"""What the browser asks of this Odoo for Dooservice: the bot, the pieces of its messages, the project status."""

from odoo import api, models

from ..constants import BOT_PARTNER, GROUP_ASK, GROUP_REQUEST
from ..services.card_actions import CardActions
from ..services.card_payload import CardPayload
from ..services.client import BusinessClient, BusinessError
from ..services.status_cache import StatusCache
from ..services.status_line import StatusLine
from ..services.wording import Wording


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def dooservice_brain_bot(self):
        """Dooservice's partner, for the browser to know its messages; nothing for who may not ask."""
        return self.env.ref(BOT_PARTNER).id if self.env.user.has_group(GROUP_ASK) else False

    @api.model
    def dooservice_brain_status(self):
        """What the bulb says before a ticket is opened: whether it can be, and when the consultancy answers."""
        if not self.env.user.has_group(GROUP_ASK):
            return {"allowed": False}
        found = {"allowed": True, "can_request": self.env.user.has_group(GROUP_REQUEST), "ready": False, "line": ""}
        try:
            status = StatusCache.of(self.env.cr.dbname, BusinessClient())
        except BusinessError as error:
            return {**found, "line": Wording.refusal(error.code, self.env.user.lang or "")}
        if not status.get("enabled"):
            return {**found, "line": Wording.refusal("business_disabled", self.env.user.lang or "")}
        return {**found, "ready": True, "line": StatusLine(self.env).of(status)}

    @api.model
    def dooservice_brain_cards(self, message_ids):
        return CardPayload(self.env).of(message_ids)

    @api.model
    def dooservice_brain_act(self, message_id, card_id, action, value=None, label=""):
        message = CardActions(self.env).act(message_id, card_id, action, value, label)
        return CardPayload(self.env).of([message.id]).get(message.id)
