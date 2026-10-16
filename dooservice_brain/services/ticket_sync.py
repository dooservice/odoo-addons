"""Open tickets kept in step with the platform: what people wrote here goes out, what it answered comes in.

Run by the sync task every two minutes, and sooner when someone writes. The task passes a
checkpoint, a commit, taken after each ticket so one that fails leaves the others done.
"""

from odoo import fields
from odoo.tools import html2plaintext

from ..constants import CLOSED_STATES, TEXT_MAX_CHARACTERS, TICKETS_PER_RUN
from .bot_posting import BotPosting
from .client import BusinessClient, BusinessError
from .remote_values import RemoteValues
from .ticket_update import TicketUpdate
from .wording import Wording


class TicketSync:
    def __init__(self, env, client=None, checkpoint=None):
        self.env = env
        self.client = client or BusinessClient()
        self.checkpoint = checkpoint

    def run(self):
        tickets = (
            self.env["dooservice.ticket"]
            .sudo()
            .search(
                [("state", "not in", CLOSED_STATES), ("channel_id", "!=", False), ("remote_number", ">", 0)],
                order="last_sync asc, id asc",
                limit=TICKETS_PER_RUN,
            )
        )
        if not tickets or not self.client.configured:
            return
        for ticket in tickets:
            self.one(ticket)
            if self.checkpoint:
                self.checkpoint()

    def one(self, ticket):
        now = fields.Datetime.now()
        self.outgoing(ticket)
        try:
            outcome = self.client.messages(ticket.remote_number, RemoteValues.since(ticket.last_sync))
        except BusinessError:
            return
        TicketUpdate(self.env).apply(ticket, outcome)
        ticket.last_sync = now

    def outgoing(self, ticket):
        pending = (
            self.env["mail.message"]
            .sudo()
            .search(
                [
                    ("model", "=", "mail.channel"),
                    ("res_id", "=", ticket.channel_id.id),
                    ("dooservice_pending", "=", True),
                ],
                order="id",
            )
        )
        for message in pending:
            message.dooservice_pending = False
            self.carry(ticket, message)

    def carry(self, ticket, message):
        user = message.author_id.user_ids[:1]
        body = {
            "text": html2plaintext(message.body or "").strip()[:TEXT_MAX_CHARACTERS],
            "user_login": user.login,
            "user_name": user.name or message.author_id.name,
        }
        if not body["text"]:
            return
        try:
            outcome = self.client.send(ticket.remote_number, body)
        except BusinessError as error:
            BotPosting(self.env).post(ticket.channel_id, Wording.refusal(error.code, user.lang or ""))
            return
        TicketUpdate(self.env).apply(ticket, outcome)
