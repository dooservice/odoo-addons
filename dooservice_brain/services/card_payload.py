"""What the browser draws under a message of Dooservice: its pieces, what was done with them, and who may press them."""

from odoo.exceptions import AccessError

from ..constants import CLOSED_STATES, GROUP_RESPONSIBLE
from .card_guard import CardGuard


class CardPayload:
    def __init__(self, env):
        self.env = env

    def of(self, message_ids):
        found = {}
        for message_id in message_ids:
            try:
                message, ticket = CardGuard(self.env).message(message_id)
            except AccessError:
                continue
            found[message.id] = self.one(message, ticket)
        return found

    def one(self, message, ticket):
        return {
            "cards": message.dooservice_cards,
            "state": message.dooservice_card_state or {},
            "can_approve": self.env.user.has_group(GROUP_RESPONSIBLE),
            "closed": ticket.state in CLOSED_STATES,
        }
