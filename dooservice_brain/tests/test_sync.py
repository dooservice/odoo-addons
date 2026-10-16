"""What people write goes to the platform by the sync task, and what it answers comes back once."""

from odoo.tests import tagged

from odoo.addons.dooservice_brain.services.ticket_sync import TicketSync

from .common import TicketCase
from .platform import ESCALATED, FOR_RESPONSIBLE, REPLY, FakePlatform


@tagged("post_install", "-at_install")
class TestSync(TicketCase):
    def test_a_message_waits_as_pending_until_the_task_carries_it(self):
        ticket, platform = self.opened(self.ana)
        platform.answers["send"] = lambda number, body: {
            "ticket": {"number": number, "state": "running"},
            "messages": [REPLY],
        }

        written = self.say(self.ana, ticket.channel_id, "Why?")
        pending = written.dooservice_pending

        TicketSync(self.env, platform).run()

        sent = platform.asked[-2]
        self.assertTrue(pending)
        self.assertEqual(
            (sent[0], sent[1][0], sent[1][1]["text"], sent[1][1]["user_login"]), ("send", 1, "Why?", "ana")
        )
        self.assertEqual(ticket.state, "running")
        answer = self.said(ticket.channel_id)
        self.assertEqual((answer.author_id, answer.dooservice_remote_id), (self.bot, 202))
        self.assertEqual(answer.dooservice_cards[0]["id"], "c0")
        self.assertFalse(written.dooservice_pending)

    def test_the_same_remote_message_is_posted_once(self):
        ticket, platform = self.opened(self.ana)
        platform.answers["messages"] = lambda number, since: {"ticket": {}, "messages": [REPLY]}

        TicketSync(self.env, platform).run()
        TicketSync(self.env, platform).run()

        posted = self.env["mail.message"].search_count(
            [("res_id", "=", ticket.channel_id.id), ("dooservice_remote_id", "=", 202)]
        )
        self.assertEqual(posted, 1)
        self.assertTrue(ticket.last_sync)
        self.assertTrue(platform.asked[-1][1][1])

    def test_the_consultants_answer_carries_her_name_and_the_deadline(self):
        ticket, platform = self.opened(self.ana)
        platform.answers["messages"] = lambda number, since: ESCALATED

        TicketSync(self.env, platform).run()

        self.assertEqual((ticket.state, str(ticket.deadline)), ("waiting_consultant", "2026-10-16 18:00:00"))
        self.assertIn("Julia Soto", self.said(ticket.channel_id).body)

    def test_the_responsible_joins_when_the_ticket_waits_for_them(self):
        ticket, platform = self.opened(self.eva, kind="change")
        platform.answers["messages"] = lambda number, since: FOR_RESPONSIBLE

        TicketSync(self.env, platform).run()

        self.assertIn(self.rosa.partner_id, ticket.channel_id.channel_member_ids.partner_id)
        self.assertNotIn(self.ana.partner_id, ticket.channel_id.channel_member_ids.partner_id)

    def test_a_refusal_is_put_in_words_and_not_retried(self):
        ticket, platform = self.opened(self.ana)
        self.say(self.ana, ticket.channel_id, "Why?")
        platform.refusal = "ai_limit_reached"

        TicketSync(self.env, platform).run()

        self.assertIn("reached its limit", self.said(ticket.channel_id).body)
        self.assertFalse(self.env["mail.message"].search([("dooservice_pending", "=", True)]))

    def test_closed_tickets_and_an_unconfigured_platform_are_left_alone(self):
        ticket, platform = self.opened(self.ana)
        ticket.sudo().state = "closed"
        asked_before = len(platform.asked)

        TicketSync(self.env, platform).run()
        self.env["dooservice.ticket"]._sync_open()

        self.assertEqual(len(platform.asked), asked_before)

    def test_someone_outside_the_group_is_told_and_nothing_waits(self):
        ticket, _platform = self.opened(self.ana)
        ticket.channel_id.sudo().add_members(partner_ids=self.luis.partner_id.ids, post_joined_message=False)

        self.say(self.luis, ticket.channel_id, "Hello")

        self.assertIn("do not have access", self.said(ticket.channel_id).body)
        self.assertFalse(self.env["mail.message"].search([("dooservice_pending", "=", True)]))
        self.assertEqual(FakePlatform().names(), [])
