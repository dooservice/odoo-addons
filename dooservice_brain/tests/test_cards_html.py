"""In Odoo 16 the pieces are signed links in the message; a pressed one is written as done."""

from odoo.tests import tagged

from odoo.addons.dooservice_brain.services.card_actions import CardActions
from odoo.addons.dooservice_brain.services.cards_html import CardsHtml
from odoo.addons.dooservice_brain.services.ticket_sync import TicketSync

from .common import TicketCase
from .platform import CLOSED, RESOLVED


@tagged("post_install", "-at_install")
class TestCardsHtml(TicketCase):
    def test_the_message_carries_signed_links_and_then_what_was_pressed(self):
        ticket, platform = self.opened(self.ana)
        platform.answers["messages"] = lambda number, since: {"ticket": {}, "messages": [RESOLVED]}
        TicketSync(self.env, platform).run()
        message = self.said(ticket.channel_id)
        token = CardsHtml.token(self.env, message.id, "c0", "yes", "", "Yes, close")

        self.assertIn(token, message.body)
        platform.answers["act"] = lambda number, body: CLOSED
        CardActions(self.env(user=self.ana), platform).act(message.id, "c0", "yes", None, "Yes, close")

        self.assertNotIn(token, message.body)
        self.assertIn("✓ Yes, close", message.body)

    def test_a_closed_ticket_offers_the_link_to_a_new_one(self):
        ticket, platform = self.opened(self.ana)
        ticket.sudo().state = "closed"

        self.say(self.ana, ticket.channel_id, "One more thing")

        answer = self.said(ticket.channel_id)
        self.assertIn(f"action=dooservice_brain.new_ticket&amp;continues={ticket.id}", answer.body)
        self.assertIn("Open a new linked ticket", answer.body)
