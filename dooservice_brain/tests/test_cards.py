"""The pieces under an answer do something only when pressed, and only once.

A draft is sent as one request however many times it is pressed; cancelled, it leaves
nothing. Someone who may only ask leaves it with an administrator, and a chart counts only
what the person may read.
"""

from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user, tagged

from odoo.addons.dooservice_brain.services.answering import Answering
from odoo.addons.dooservice_brain.services.card_actions import CardActions
from odoo.addons.dooservice_brain.services.chart_counting import ChartCounting

from .platform import FakePlatform
from .test_requests import READ_BACK

DRAFTED = {
    "called": True,
    "answer": "I can ask for that board.",
    "sources": [],
    "found": True,
    "suggest_request": True,
    "cards": [{"type": "draft", "title": "Orders by channel", "text": "A board of orders by channel"}],
}


@tagged("post_install", "-at_install")
class TestCards(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ana = new_test_user(cls.env, "ana", groups="base.group_user,dooservice_brain.group_request")
        cls.eva = new_test_user(cls.env, "eva", groups="base.group_user,dooservice_brain.group_ask")

    def answer_for(self, user, platform):
        self.env["res.users"].with_user(user).dooservice_brain_open("sale.order")
        channel = self.env["res.users"].with_user(user)._dooservice_brain_chat()
        channel.with_user(user).message_post(
            body="A board, please", message_type="comment", subtype_xmlid="mail.mt_comment"
        )
        question = self.env["dooservice.brain.question"].search([("user_id", "=", user.id)], limit=1)
        Answering(self.env, platform).answer(question)
        return self.env["mail.message"].search([("model", "=", channel._name), ("res_id", "=", channel.id)], limit=1)

    def draft_of(self, message):
        return next(card for card in message.dooservice_cards if card["type"] == "draft")

    def test_the_draft_is_read_back_and_kept_with_the_answer(self):
        message = self.answer_for(self.ana, FakePlatform({"ask": DRAFTED, "understand": READ_BACK}))

        draft = self.draft_of(message)
        self.assertEqual((draft["remote_id"], draft["rows"]), (READ_BACK["id"], 1200))
        self.assertFalse(self.env["dooservice.brain.request"].search([]))

    def test_sending_twice_makes_one_request(self):
        platform = FakePlatform({"ask": DRAFTED, "understand": READ_BACK, "submit": {**READ_BACK, "state": "queued"}})
        message = self.answer_for(self.ana, platform)
        actions = CardActions(self.env(user=self.ana), platform)

        actions.act(message.id, self.draft_of(message)["id"], "send")
        actions.act(message.id, self.draft_of(message)["id"], "send")

        sent = self.env["dooservice.brain.request"].search([])
        self.assertEqual((len(sent), sent.state, sent.message_id), (1, "queued", message))
        self.assertEqual([name for name, _args in platform.asked].count("submit"), 1)

    def test_cancelling_leaves_nothing(self):
        platform = FakePlatform({"ask": DRAFTED, "understand": READ_BACK})
        message = self.answer_for(self.ana, platform)

        CardActions(self.env(user=self.ana), platform).act(message.id, self.draft_of(message)["id"], "cancel")

        self.assertFalse(self.env["dooservice.brain.request"].search([]))
        self.assertEqual(platform.asked[-1][0], "cancel")

    def test_who_may_only_ask_leaves_it_with_an_administrator(self):
        platform = FakePlatform({"ask": DRAFTED, "understand": READ_BACK})
        message = self.answer_for(self.eva, platform)

        CardActions(self.env(user=self.eva), platform).act(message.id, self.draft_of(message)["id"], "send")

        asked = self.env["dooservice.brain.request"].search([])
        self.assertEqual((asked.state, asked.requested_by), ("draft", self.eva))
        self.assertNotIn("submit", [name for name, _args in platform.asked])

    def test_someone_else_cannot_press_it(self):
        platform = FakePlatform({"ask": DRAFTED, "understand": READ_BACK})
        message = self.answer_for(self.ana, platform)

        with self.assertRaises(AccessError):
            CardActions(self.env(user=self.eva), platform).act(message.id, self.draft_of(message)["id"], "send")

    def test_a_chart_counts_only_what_the_person_may_read(self):
        card = {"type": "chart", "model": "res.partner", "group_by": "is_company"}
        outsider = new_test_user(self.env, "pia", groups="base.group_portal")

        counted = ChartCounting(self.env(user=self.ana)).count(card)
        refused = ChartCounting(self.env(user=outsider)).count({**card, "model": "ir.cron", "group_by": "active"})

        self.assertTrue(counted["groups"])
        self.assertEqual(refused, {"denied": "access"})
