"""The pieces posted under an answer: its sources, what the platform proposed, and a rating.

A draft is read back by the platform before it is shown, so the person sees what was
understood; nothing is sent until they press «Send». The line saying which model answers
goes only under the first answer of a chat, not under every one.
"""

from odoo import _
from ..constants import BOT_PARTNER, DRAFT_CARD, FEEDBACK_CARD, META_CARD, SOURCES_CARD
from .draft_reading import DraftReading


class AnswerCards:
    def __init__(self, env, client):
        self.env = env
        self.client = client

    def of(self, question, result, footer):
        cards = []
        sources = result.get("sources") or []
        if sources:
            items = [
                _("%(process)s · step %(step)s", process=source.get("name"), step=source.get("step"))
                for source in sources
            ]
            cards.append({"type": SOURCES_CARD, "items": items})
        for card in result.get("cards") or []:
            cards.append(self.drafted(question, card) if card.get("type") == DRAFT_CARD else card)
        if result.get("found"):
            cards.append({"type": FEEDBACK_CARD, "question": question.text})
        if self.first_answer(question.channel_id):
            cards.append({"type": META_CARD, "text": footer})
        return [{**card, "id": card.get("id") or f"c{index}"} for index, card in enumerate(cards)]

    def drafted(self, question, card):
        """What the platform understood, read back now; the person sends it, or not."""
        read = DraftReading(self.client).read(
            question.user_id, card.get("text") or question.text, question.screen_model, card.get("title") or ""
        )
        return {**card, **read}

    def first_answer(self, channel):
        bot = self.env.ref(BOT_PARTNER)
        earlier = (
            self.env["mail.message"]
            .sudo()
            .search_count(
                [
                    ("model", "=", channel._name),
                    ("res_id", "=", channel.id),
                    ("author_id", "=", bot.id),
                    ("dooservice_cards", "!=", False),
                ]
            )
        )
        return not earlier
