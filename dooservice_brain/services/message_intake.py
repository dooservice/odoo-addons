"""A message written in a ticket's chat: kept for the sync task to carry to the platform.

Dooservice's own messages, choices said from a piece, and chats that are no ticket are left
alone. A closed ticket takes no more: the bot says so and offers a new ticket linked to it.
"""

from ..constants import BOT_PARTNER, CLOSED_STATES, CONTINUE_CARD, GROUP_ASK, SYNC_CRON
from .bot_posting import BotPosting
from .wording import Wording


class MessageIntake:
    def __init__(self, env):
        self.env = env

    def receive(self, channel, message):
        if self.env.context.get("dooservice_bot") or self.env.context.get("dooservice_said"):
            return
        bot = self.env.ref(BOT_PARTNER, raise_if_not_found=False)
        if not bot or message.message_type != "comment" or message.author_id == bot:
            return
        ticket = self.env["dooservice.ticket"].sudo().search([("channel_id", "=", channel.id)], limit=1)
        if not ticket:
            return
        user = message.author_id.user_ids[:1]
        if not user or not user.has_group(GROUP_ASK):
            BotPosting(self.env).post(
                channel, self.env._("You do not have access to Dooservice. Ask your administrator.")
            )
            return
        if ticket.state in CLOSED_STATES:
            self.refuse_closed(ticket, user)
            return
        message.sudo().dooservice_pending = True
        self.env.ref(SYNC_CRON).sudo()._trigger()

    def refuse_closed(self, ticket, user):
        card = {"id": "c0", "type": CONTINUE_CARD, "ticket": ticket.id, "number": ticket.number}
        BotPosting(self.env).post(ticket.channel_id, Wording.refusal("ticket_closed", user.lang or ""), [card])
