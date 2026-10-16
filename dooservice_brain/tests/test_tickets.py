"""A ticket of each kind is opened with its own chat; who sees it depends on their group."""

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.dooservice_brain.services.status_line import StatusLine

from .common import TicketCase
from .platform import STATUS, FakePlatform


@tagged("post_install", "-at_install")
class TestTickets(TicketCase):
    def test_each_kind_opens_its_own_chat_with_the_screen_attached(self):
        for kind in ("question", "incident", "change"):
            ticket, platform = self.opened(self.ana, kind=kind)

            sent = platform.asked[0][1][0]
            self.assertEqual(
                (sent["kind"], sent["record_ref"], sent["user_can_request"]),
                (kind, f"res.partner,{self.record.id}", True),
            )
            self.assertEqual(sent["language"], "en")
            self.assertEqual(ticket.kind, kind)
            self.assertEqual(ticket.channel_id.channel_type, "group")
            self.assertEqual(ticket.channel_id.name, f"{ticket.number} · {ticket.title}")
            self.assertEqual(ticket.channel_id.channel_member_ids.partner_id, self.ana.partner_id | self.bot)

    def test_the_chat_starts_with_the_screen_the_words_and_the_answer(self):
        ticket, _platform = self.opened(self.eva)

        messages = self.said(ticket.channel_id, limit=10).sorted("id")
        self.assertIn("Contact Comercial Los Andes", messages[0].body)
        self.assertEqual((messages[1].author_id, messages[1].dooservice_pending), (self.eva.partner_id, False))
        self.assertEqual((messages[2].author_id, messages[2].dooservice_remote_id), (self.bot, 101))
        self.assertEqual(ticket.number, "T-0001")
        self.assertEqual(ticket.process_name, "Wholesale")

    def test_who_may_only_ask_says_so_to_the_platform(self):
        _ticket, platform = self.opened(self.eva, kind="change")

        sent = platform.asked[0][1][0]
        self.assertEqual((sent["user_can_request"], sent["user_is_responsible"]), (False, False))

    def test_a_refusal_opens_nothing(self):
        with self.assertRaises(UserError) as caught:
            self.opened(self.ana, FakePlatform(refusal="business_disabled"))

        self.assertIn("not turned on", str(caught.exception))
        self.assertFalse(self.env["dooservice.ticket"].search([]))

    def test_someone_outside_the_group_cannot_open(self):
        with self.assertRaises(UserError):
            self.opened(self.luis)

    def test_a_linked_ticket_names_the_one_it_continues(self):
        first, _platform = self.opened(self.ana)
        first.sudo().state = "closed"

        second, platform = self.opened(self.ana, continues=first.id)

        self.assertEqual(platform.asked[0][1][0]["continues"], first.remote_number)
        self.assertEqual(second.continues_id, first)
        self.assertIn("continues T-0001", self.said(second.channel_id, limit=10).sorted("id")[0].body)

    def test_the_responsible_sees_the_teams_tickets_and_others_only_theirs(self):
        self.opened(self.ana)
        self.opened(self.eva)

        Ticket = self.env["dooservice.ticket"]
        self.assertEqual(len(Ticket.with_user(self.rosa).search([])), 2)
        self.assertEqual(Ticket.with_user(self.eva).search([]).user_id, self.eva)
        self.assertEqual(Ticket.with_user(self.ana).search([]).user_id, self.ana)

    def test_the_header_names_kind_state_and_process(self):
        ticket, _platform = self.opened(self.ana)

        header = self.env["dooservice.ticket"].with_user(self.ana).header_of(ticket.channel_id.id)

        self.assertEqual(
            (header["number"], header["kind_label"], header["state_label"]), ("T-0001", "Incident", "Open")
        )
        self.assertEqual((header["process"], header["closed"]), ("Wholesale", False))
        self.assertFalse(self.env["dooservice.ticket"].header_of(0))

    def test_the_status_line_says_when_the_consultancy_answers(self):
        line = StatusLine(self.env).of(STATUS)

        self.assertEqual(line, "Your consultancy answers Mon–Fri 09:00–18:00 within 4 working hours.")
