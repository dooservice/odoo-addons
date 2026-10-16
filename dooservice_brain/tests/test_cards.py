"""The pieces under a message move the ticket only when pressed, once, and by who may press them.

«Yes, close» closes the ticket; the closed chat then refuses what is written and offers a
new ticket linked to it. An approval is a responsible's alone.
"""

from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged

from odoo.addons.dooservice_brain.services.card_actions import CardActions
from odoo.addons.dooservice_brain.services.card_payload import CardPayload
from odoo.addons.dooservice_brain.services.ticket_sync import TicketSync

from .common import TicketCase
from .platform import APPROVAL, CLOSED, RESOLVED


@tagged("post_install", "-at_install")
class TestCards(TicketCase):
    def with_card(self, user, card_message, kind="incident"):
        ticket, platform = self.opened(user, kind=kind)
        platform.answers["messages"] = lambda number, since: {"ticket": {}, "messages": [card_message]}
        TicketSync(self.env, platform).run()
        return ticket, platform, self.said(ticket.channel_id)

    def test_yes_close_closes_the_ticket_and_says_so(self):
        ticket, platform, message = self.with_card(self.ana, RESOLVED)
        platform.answers["act"] = lambda number, body: CLOSED

        CardActions(self.env(user=self.ana), platform).act(message.id, "c0", "yes", None, "Yes, close")

        sent = platform.asked[-1][1][1]
        self.assertEqual((sent["card"], sent["action"], sent["value"], sent["user_login"]), ("c0", "yes", None, "ana"))
        self.assertEqual(ticket.state, "closed")
        self.assertEqual(message.dooservice_card_state["c0"]["done"], "yes")
        messages = self.said(ticket.channel_id, limit=2).sorted("id")
        self.assertIn("Yes, close", messages[0].body)
        self.assertEqual((messages[1].message_type, messages[1].dooservice_remote_id), ("notification", 404))

    def test_a_piece_answers_once(self):
        _ticket, platform, message = self.with_card(self.ana, RESOLVED)
        actions = CardActions(self.env(user=self.ana), platform)

        actions.act(message.id, "c0", "no")
        with self.assertRaises(UserError):
            actions.act(message.id, "c0", "yes")

        self.assertEqual(platform.names().count("act"), 1)

    def test_a_closed_ticket_refuses_what_is_written_and_offers_a_new_one(self):
        ticket, platform, message = self.with_card(self.ana, RESOLVED)
        platform.answers["act"] = lambda number, body: CLOSED
        CardActions(self.env(user=self.ana), platform).act(message.id, "c0", "yes")

        self.say(self.ana, ticket.channel_id, "One more thing")

        answer = self.said(ticket.channel_id)
        self.assertEqual(answer.author_id, self.bot)
        self.assertIn("open a new one linked", answer.body)
        self.assertEqual(answer.dooservice_cards[0]["type"], "continue")
        self.assertEqual(answer.dooservice_cards[0]["ticket"], ticket.id)
        self.assertFalse(self.env["mail.message"].search([("dooservice_pending", "=", True)]))
        self.assertTrue(CardPayload(self.env(user=self.ana)).of([answer.id])[answer.id]["closed"])

    def test_only_a_responsible_approves(self):
        ticket, platform, message = self.with_card(self.eva, APPROVAL, kind="change")
        ticket.channel_id.sudo().add_members(partner_ids=self.rosa.partner_id.ids, post_joined_message=False)

        with self.assertRaises(AccessError):
            CardActions(self.env(user=self.eva), platform).act(message.id, "c0", "approve")
        CardActions(self.env(user=self.rosa), platform).act(message.id, "c0", "approve", None, "Approve")

        self.assertEqual(platform.asked[-1][1][1]["user_login"], "rosa")
        payload = CardPayload(self.env(user=self.eva)).of([message.id])[message.id]
        self.assertEqual((payload["can_approve"], payload["state"]["c0"]["done"]), (False, "approve"))

    def test_someone_else_cannot_press_it_nor_see_it(self):
        _ticket, platform, message = self.with_card(self.ana, RESOLVED)

        with self.assertRaises(AccessError):
            CardActions(self.env(user=self.eva), platform).act(message.id, "c0", "yes")

        self.assertEqual(CardPayload(self.env(user=self.eva)).of([message.id]), {})

    def test_a_correction_needs_words(self):
        _ticket, platform, message = self.with_card(
            self.ana, {**RESOLVED, "cards": [{"type": "understood"}]}, kind="change"
        )

        with self.assertRaises(UserError):
            CardActions(self.env(user=self.ana), platform).act(message.id, "c0", "correct", "")
        CardActions(self.env(user=self.ana), platform).act(
            message.id, "c0", "correct", "Only wholesale customers", "Correct"
        )

        self.assertEqual(platform.asked[-1][1][1]["value"], "Only wholesale customers")
