"""Which piece a person acts on, and whether they may: a message of Dooservice, in a ticket's chat of theirs."""

from odoo import _
from odoo.exceptions import AccessError, UserError

from ..constants import BOT_PARTNER, CARD_ACTIONS, GROUP_ASK, GROUP_RESPONSIBLE, RESPONSIBLE_CARDS


class CardGuard:
    def __init__(self, env):
        self.env = env

    def message(self, message_id):
        message = self.env["mail.message"].sudo().browse(int(message_id)).exists()
        if (
            not self.env.user.has_group(GROUP_ASK)
            or not message
            or message.author_id != self.env.ref(BOT_PARTNER)
            or not message.dooservice_cards
        ):
            raise AccessError(_("This piece is not in a ticket of yours."))
        channel = self.env[message.model].sudo().browse(message.res_id).exists()
        if not channel or self.env.user.partner_id not in channel.channel_member_ids.partner_id:
            raise AccessError(_("This piece is not in a ticket of yours."))
        ticket = self.env["dooservice.ticket"].sudo().search([("channel_id", "=", channel.id)], limit=1)
        if not ticket:
            raise AccessError(_("This piece is not in a ticket of yours."))
        return message, ticket

    def card(self, message, card_id, action):
        card = next((card for card in message.dooservice_cards if card.get("id") == card_id), None)
        if not card or action not in CARD_ACTIONS.get(card.get("type"), ()):
            raise UserError(_("This piece cannot do that."))
        if card["type"] in RESPONSIBLE_CARDS and not self.env.user.has_group(GROUP_RESPONSIBLE):
            raise AccessError(_("Only a Dooservice responsible decides this."))
        return card

    def lock(self, message):
        """Two clicks at once wait for each other, so the second finds the first one done."""
        self.env.cr.execute("SELECT id FROM mail_message WHERE id = %s FOR UPDATE", (message.id,))
        message.invalidate_recordset(["dooservice_cards", "dooservice_card_state"])
