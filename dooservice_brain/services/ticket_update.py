"""What the platform answered about a ticket, taken in: its state, its messages, and who its chat now needs."""

from ..constants import GROUP_RESPONSIBLE
from .bot_posting import BotPosting
from .remote_values import RemoteValues


class TicketUpdate:
    def __init__(self, env):
        self.env = env

    def apply(self, ticket, outcome):
        remote = outcome.get("ticket") or {}
        if remote:
            ticket.sudo().write(RemoteValues.of(remote))
            self.rename(ticket)
        posted = BotPosting(self.env).remote(ticket, outcome.get("messages") or [])
        if ticket.waiting_for == "responsible":
            self.invite_responsibles(ticket)
        return posted

    def rename(self, ticket):
        wanted = ticket.channel_name()
        if ticket.channel_id and ticket.channel_id.name != wanted:
            ticket.channel_id.sudo().name = wanted

    def invite_responsibles(self, ticket):
        """The Dooservice responsibles join the chat the first time the ticket waits for one of them."""
        group = self.env.ref(GROUP_RESPONSIBLE, raise_if_not_found=False)
        if not group or not ticket.channel_id:
            return
        partners = group.users.filtered("active").partner_id - ticket.channel_id.channel_member_ids.partner_id
        if partners:
            ticket.channel_id.sudo()._add_members(partners=partners, post_joined_message=False)
