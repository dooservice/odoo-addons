"""What a person does with a piece of an answer, once: choose, send, cancel, correct, rate or retry.

Each piece remembers what was done with it on its message, so a second click finds it done
and nothing is sent twice. A choice is said in the chat as the person's own message, and
that message is the next question.
"""

from odoo.exceptions import UserError

from ..constants import ANSWER_CRON, QUESTION_MAX_CHARACTERS, RATINGS
from .card_guard import CardGuard
from .client import AssistantClient, AssistantError
from .draft_reading import DraftReading
from .draft_sending import DraftSending
from .wording import Wording


class CardActions:
    def __init__(self, env, client=None):
        self.env = env
        self.client = client or AssistantClient()
        self.drafts = DraftSending(env, self.client)

    def act(self, message_id, card_id, action, value=None):
        guard = CardGuard(self.env)
        message, channel = guard.message(message_id)
        guard.lock(message)
        card = guard.card(message, card_id, action)
        state = dict(message.dooservice_card_state or {})
        mine = state.get(card_id) or {}
        if mine.get("done") and action != "cancel_request":
            return message
        state[card_id] = getattr(self, action)(message, channel, card, value, mine)
        message.dooservice_card_state = state
        return message

    def choose(self, message, channel, card, value, mine):
        said = self.said(card, value)
        channel.with_user(self.env.user).message_post(
            body=said, message_type="comment", subtype_xmlid="mail.mt_comment"
        )
        return {"done": "choose", "value": said}

    def said(self, card, value):
        if card["type"] == "field":
            said = str(value or "").strip()[:QUESTION_MAX_CHARACTERS]
        else:
            chosen = set(value if isinstance(value, list) else [value])
            said = ", ".join(option["label"] for option in card.get("options", []) if option["value"] in chosen)
        if not said:
            raise UserError(self.env._("Choose an option first."))
        return said

    def send(self, message, channel, card, value, mine):
        return self.drafts.send(message, card)

    def cancel(self, message, channel, card, value, mine):
        self.drafts.cancel(card)
        return {"done": "cancel"}

    def correct(self, message, channel, card, value, mine):
        text = str(value or "").strip()[:QUESTION_MAX_CHARACTERS]
        if not text:
            raise UserError(self.env._("Say what to change first."))
        self.drafts.cancel(card)
        read = DraftReading(self.client).read(
            self.env.user, text, self.env.user.dooservice_brain_screen, card.get("title") or ""
        )
        message.dooservice_cards = [
            {**item, **read} if item["id"] == card["id"] else item for item in message.dooservice_cards
        ]
        return {}

    def cancel_request(self, message, channel, card, value, mine):
        if not mine.get("request"):
            raise UserError(self.env._("This draft was not sent."))
        self.drafts.cancel_request(mine["request"])
        return mine

    def rate(self, message, channel, card, value, mine):
        if value not in RATINGS:
            raise UserError(self.env._("Rate it up or down."))
        try:
            self.client.feedback(card.get("question") or "", value, self.env.user.name)
        except AssistantError as error:
            raise UserError(Wording.refusal(error.code, self.env.user.lang or "")) from error
        return {"done": "rate", "value": value}

    def retry(self, message, channel, card, value, mine):
        Question = self.env["dooservice.brain.question"].sudo()
        asked = Question.browse(card.get("question") or 0).exists()
        if not asked or asked.user_id != self.env.user:
            raise UserError(self.env._("This question is not yours."))
        Question.create(
            {
                "channel_id": asked.channel_id.id,
                "message_id": asked.message_id.id,
                "user_id": asked.user_id.id,
                "text": asked.text,
                "screen_model": asked.screen_model,
            }
        )
        self.env.ref(ANSWER_CRON).sudo()._trigger()
        return {"done": "retry"}
