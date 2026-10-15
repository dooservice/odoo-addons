"""A message to Dooservice becomes a question, and its answer comes back in the same chat.

Only people in the assistant's group are answered; Dooservice's own messages and other
chats are left alone. The answer says what it stands on and which model wrote it.
"""

from unittest.mock import patch

from odoo.tests import TransactionCase, new_test_user, tagged

from odoo.addons.dooservice_brain.services.answering import Answering
from odoo.addons.dooservice_brain.services.status_cache import StatusCache

from .platform import FakePlatform

ANSWERED = {
    "called": True,
    "answer": "Sales confirms the quotation.",
    "sources": [{"process": "quote-to-cash", "name": "Quote to cash", "step": 2, "title": "Confirm"}],
    "found": True,
    "suggest_request": False,
}


@tagged("post_install", "-at_install")
class TestChat(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bot = cls.env.ref("dooservice_brain.partner_dooservice")
        cls.ana = new_test_user(cls.env, "ana", groups="base.group_user,dooservice_brain.group_ask")
        cls.luis = new_test_user(cls.env, "luis", groups="base.group_user")

    def setUp(self):
        super().setUp()
        StatusCache.forget(self.env.cr.dbname)

    def chat_of(self, user):
        self.env["res.users"].with_user(user).dooservice_brain_open("sale.order")
        return self.env["res.users"].with_user(user)._dooservice_brain_chat()

    def say(self, user, text):
        channel = self.chat_of(user)
        channel.with_user(user).message_post(body=text, message_type="comment", subtype_xmlid="mail.mt_comment")
        return channel

    def answered(self, platform):
        question = self.env["dooservice.brain.question"].search([], limit=1)
        Answering(self.env, platform).answer(question)
        return question

    def last_said(self, channel):
        return self.env["mail.message"].search([("model", "=", "discuss.channel"), ("res_id", "=", channel.id)], limit=1)

    def test_the_answer_cites_its_steps_and_who_answered(self):
        channel = self.say(self.ana, "How is an order confirmed?")
        platform = FakePlatform({"ask": ANSWERED})

        question = self.answered(platform)

        said = self.last_said(channel)
        self.assertEqual(said.author_id, self.bot)
        self.assertIn("Quote to cash · step 2", said.body)
        self.assertIn("Claude Haiku 5.5", said.body)
        self.assertEqual(question.state, "answered")
        self.assertEqual(platform.asked[0][1][:2], ("How is an order confirmed?", "sale.order"))

    def test_someone_outside_the_group_is_told_and_nothing_is_asked(self):
        self.luis.dooservice_brain_screen = False
        channel = self.env["res.users"].with_user(self.luis)._dooservice_brain_chat()
        channel.with_user(self.luis).message_post(body="Hello", message_type="comment", subtype_xmlid="mail.mt_comment")

        self.assertFalse(self.env["dooservice.brain.question"].search([]))
        self.assertIn("do not have access", self.last_said(channel).body)

    def test_with_nothing_reviewed_it_does_not_guess(self):
        channel = self.say(self.ana, "Who approves discounts?")

        self.answered(FakePlatform({"ask": {"called": False}}))

        self.assertIn("Nobody has reviewed", self.last_said(channel).body)

    def test_a_refusal_is_put_in_words(self):
        channel = self.say(self.ana, "Who approves discounts?")

        question = self.answered(FakePlatform(refusal="ai_limit_reached"))

        self.assertIn("reached its limit", self.last_said(channel).body)
        self.assertEqual((question.state, question.error), ("failed", "ai_limit_reached"))

    def test_a_plan_on_hold_is_said_in_its_own_words(self):
        channel = self.say(self.ana, "Who approves discounts?")

        self.answered(FakePlatform(refusal="assistant_on_hold"))

        self.assertIn("plan is on hold", self.last_said(channel).body)

    def test_dooservice_does_not_answer_itself(self):
        channel = self.chat_of(self.ana)
        with patch.object(type(self.env["dooservice.brain.question"]), "create") as created:
            Answering(self.env, FakePlatform()).post(channel, "Hello")
        created.assert_not_called()
