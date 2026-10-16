"""A ticket opened from the bulb: the platform takes it first, then its chat is made here.

The chat is a group channel of the person and Dooservice, named after the ticket. The
screen it was opened from is said in the chat for people; the platform only gets its
reference, which it never shows to the AI.
"""

from odoo.exceptions import UserError

from ..constants import BOT_PARTNER, GROUP_ASK, GROUP_REQUEST, GROUP_RESPONSIBLE, TEXT_MAX_CHARACTERS, TICKET_KINDS
from .client import BusinessClient, BusinessError
from .remote_values import RemoteValues
from .screen_label import ScreenLabel
from .ticket_update import TicketUpdate
from .wording import Wording


class TicketOpening:
    def __init__(self, env, client=None):
        self.env = env
        self.client = client or BusinessClient()

    def open(self, kind, text, screen_model="", record_id=0, continues=None):
        user = self.env.user
        text = (text or "").strip()[:TEXT_MAX_CHARACTERS]
        if not user.has_group(GROUP_ASK):
            raise UserError(self.env._("You do not have access to Dooservice. Ask your administrator."))
        if kind not in dict(TICKET_KINDS) or not text:
            raise UserError(self.env._("Choose what the ticket is about and say what happens."))
        previous = self.previous(continues)
        try:
            outcome = self.client.open_ticket(self.body(user, kind, text, screen_model, record_id, previous))
        except BusinessError as error:
            raise UserError(Wording.refusal(error.code, user.lang or "")) from error
        ticket = self.create(user, kind, text, screen_model, record_id, previous, outcome.get("ticket") or {})
        self.start(ticket, text, screen_model, record_id)
        TicketUpdate(self.env).apply(ticket, outcome)
        return ticket

    def previous(self, continues):
        if not continues:
            return self.env["dooservice.ticket"]
        previous = self.env["dooservice.ticket"].search([("id", "=", int(continues))], limit=1)
        if not previous:
            raise UserError(self.env._("The ticket to continue is not yours."))
        return previous

    def body(self, user, kind, text, screen_model, record_id, previous):
        return {
            "kind": kind,
            "title": "",
            "text": text,
            "screen_model": screen_model or "",
            "record_ref": f"{screen_model},{int(record_id)}" if screen_model and record_id else "",
            "user_login": user.login,
            "user_name": user.name,
            "user_can_request": user.has_group(GROUP_REQUEST),
            "user_is_responsible": user.has_group(GROUP_RESPONSIBLE),
            "language": (user.lang or "en")[:2],
            "continues": previous.remote_number or None,
        }

    def create(self, user, kind, text, screen_model, record_id, previous, remote):
        ticket = (
            self.env["dooservice.ticket"]
            .sudo()
            .create(
                {
                    **RemoteValues.opened(remote, kind),
                    "title": remote.get("title") or text[:60],
                    "text": text,
                    "user_id": user.id,
                    "screen_model": screen_model or False,
                    "record_id": int(record_id or 0),
                    "continues_id": previous.id,
                }
            )
        )
        bot = self.env.ref(BOT_PARTNER)
        channel = (
            self.env["discuss.channel"].sudo().create_group([user.partner_id.id, bot.id], name=ticket.channel_name())
        )
        ticket.channel_id = channel
        return ticket

    def start(self, ticket, text, screen_model, record_id):
        """The chat begins with where it was opened from, and the person's own words."""
        screen = ScreenLabel(self.env).of(screen_model, record_id)
        opened = (
            self.env._("Ticket opened from %(screen)s", screen=screen)
            if screen
            else self.env._("Ticket opened by %(name)s", name=self.env.user.name)
        )
        if ticket.continues_id:
            opened = self.env._("%(opened)s · continues %(number)s", opened=opened, number=ticket.continues_id.number)
        ticket.notice(opened)
        ticket.channel_id.with_context(dooservice_said=True).message_post(
            body=text, message_type="comment", subtype_xmlid="mail.mt_comment"
        )
