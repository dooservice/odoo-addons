"""What a person does with a piece of a message, once: answer it, and the platform moves the ticket.

Each piece remembers what was done with it on its message, so a second click finds it done
and nothing is sent twice. The choice is said in the chat as the person's own message.
"""

from odoo.exceptions import UserError

from ..constants import CLOSED_STATES, TEXT_MAX_CHARACTERS
from .card_guard import CardGuard
from .client import BusinessClient, BusinessError
from .ticket_update import TicketUpdate
from .wording import Wording

NEEDS_TEXT = ("correct",)


class CardActions:
    def __init__(self, env, client=None):
        self.env = env
        self.client = client or BusinessClient()

    def act(self, message_id, card_id, action, value=None, label=""):
        guard = CardGuard(self.env)
        message, ticket = guard.message(message_id)
        guard.lock(message)
        guard.card(message, card_id, action)
        state = dict(message.dooservice_card_state or {})
        if state.get(card_id, {}).get("done"):
            raise UserError(Wording.refusal("card_done", self.env.user.lang or ""))
        if ticket.state in CLOSED_STATES:
            raise UserError(Wording.refusal("ticket_closed", self.env.user.lang or ""))
        text = str(value or "").strip()[:TEXT_MAX_CHARACTERS]
        if action in NEEDS_TEXT and not text:
            raise UserError(self.env._("Say what to change first."))
        self.say(ticket, label, text)
        outcome = self.send(ticket, card_id, action, text)
        state[card_id] = {"done": action, "value": text}
        message.dooservice_card_state = state
        TicketUpdate(self.env).apply(ticket, outcome)
        return message

    def say(self, ticket, label, text):
        said = ", ".join(part for part in (str(label or "").strip()[:200], text) if part)
        if said:
            ticket.channel_id.with_context(dooservice_said=True).message_post(
                body=said, message_type="comment", subtype_xmlid="mail.mt_comment"
            )

    def send(self, ticket, card_id, action, text):
        body = {
            "card": card_id,
            "action": action,
            "value": text or None,
            "user_login": self.env.user.login,
            "user_name": self.env.user.name,
        }
        try:
            return self.client.act(ticket.remote_number, body)
        except BusinessError as error:
            raise UserError(Wording.refusal(error.code, self.env.user.lang or "")) from error
