"""In Odoo 16 the pieces are links in the answer, signed for the person whose chat it is."""

from odoo.tests import tagged

from odoo.addons.dooservice_brain.services.card_actions import CardActions
from odoo.addons.dooservice_brain.services.cards_html import CardsHtml

from .platform import FakePlatform
from .test_cards import DRAFTED, TestCards
from .test_requests import READ_BACK


@tagged("post_install", "-at_install")
class TestCardsHtml(TestCards):
    def test_the_answer_carries_its_signed_links_and_then_what_was_done(self):
        platform = FakePlatform({"ask": DRAFTED, "understand": READ_BACK, "submit": {**READ_BACK, "state": "queued"}})
        message = self.answer_for(self.ana, platform)
        draft = self.draft_of(message)
        token = CardsHtml.token(self.env, self.ana.id, message.id, draft["id"], "send", "")

        self.assertIn(token, message.body)
        CardActions(self.env(user=self.ana), platform).act(message.id, draft["id"], "send")

        self.assertIn("#3", message.body)
        self.assertNotIn(token, message.body)
