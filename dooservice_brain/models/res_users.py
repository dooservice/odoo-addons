from odoo import api, fields, models

from ..constants import BOT_PARTNER, GROUP_ASK
from ..services.card_actions import CardActions
from ..services.card_guard import CardGuard
from ..services.card_payload import CardPayload
from ..services.chart_counting import ChartCounting


class ResUsers(models.Model):
    _inherit = "res.users"

    dooservice_brain_screen = fields.Char(
        string="Screen asked from",
        help="The model of the screen this person last opened the assistant from.",
    )

    @api.model
    def dooservice_brain_open(self, screen_model=""):
        """The assistant's partner, for the browser to open its chat; the screen is remembered for the next question."""
        if not self.env.user.has_group(GROUP_ASK):
            return False
        self.env.user.sudo().dooservice_brain_screen = screen_model or False
        self._dooservice_brain_chat()
        return self.env.ref(BOT_PARTNER).id

    @api.model
    def _dooservice_brain_chat(self):
        """This person's chat with Dooservice, made the first time."""
        info = self.env["mail.channel"].channel_get([self.env.ref(BOT_PARTNER).id])
        return self.env["mail.channel"].browse(info["id"])

    @api.model
    def dooservice_brain_bot(self):
        """Dooservice's partner, for the browser to know its answers; nothing for who may not ask."""
        return self.env.ref(BOT_PARTNER).id if self.env.user.has_group(GROUP_ASK) else False

    @api.model
    def dooservice_brain_cards(self, message_ids):
        return CardPayload(self.env).of(message_ids)

    @api.model
    def dooservice_brain_act(self, message_id, card_id, action, value=None):
        message = CardActions(self.env).act(message_id, card_id, action, value)
        return CardPayload(self.env).one(message)

    @api.model
    def dooservice_brain_chart(self, message_id, card_id):
        guard = CardGuard(self.env)
        message = guard.message(message_id)[0]
        card = next(
            (card for card in message.dooservice_cards if card.get("id") == card_id and card.get("type") == "chart"),
            None,
        )
        return ChartCounting(self.env).count(card) if card else {"denied": "unknown"}
