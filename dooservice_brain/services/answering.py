"""One question answered: the platform asked, the answer posted in the chat as Dooservice, with its pieces."""

from ..constants import BOT_PARTNER, ERROR_CARD, HISTORY_TURNS, RETRIABLE
from .answer_body import AnswerBody
from .answer_cards import AnswerCards
from .client import AssistantClient, AssistantError
from .status_cache import StatusCache
from .wording import Wording


class Answering:
    def __init__(self, env, client=None):
        self.env = env
        self.client = client or AssistantClient()
        self.bot = env.ref(BOT_PARTNER)

    def post(self, channel, body, cards=None):
        message = channel.sudo().message_post(
            author_id=self.bot.id, body=body, message_type="comment", silent=True, subtype_xmlid="mail.mt_comment"
        )
        if cards:
            message.sudo().dooservice_cards = cards
        return message

    def history(self, question):
        earlier = self.env["mail.message"].sudo().search(
            [
                ("model", "=", "discuss.channel"),
                ("res_id", "=", question.channel_id.id),
                ("message_type", "=", "comment"),
                ("id", "<", question.message_id.id or 0),
            ],
            order="id desc",
            limit=HISTORY_TURNS,
        )
        return [
            {"role": "assistant" if message.author_id == self.bot else "customer", "text": message.preview or ""}
            for message in reversed(earlier)
        ]

    def answer(self, question):
        lang = question.user_id.lang or "en_US"
        env = self.env(user=question.user_id, context=dict(self.env.context, lang=lang))
        language = lang[:2]
        body = AnswerBody(env)
        try:
            result = self.client.ask(question.text, question.screen_model or "", language, self.history(question))
            status = StatusCache.of(self.env.cr.dbname, self.client)
        except AssistantError as error:
            retry = [{"id": "c0", "type": ERROR_CARD, "code": error.code, "question": question.id}]
            self.post(question.channel_id, Wording.refusal(error.code, lang), retry if error.code in RETRIABLE else None)
            question.write({"state": "failed", "error": error.code})
            return
        if not result.get("called"):
            self.post(question.channel_id, body.unreviewed())
        else:
            cards = AnswerCards(env, self.client).of(question, result, body.footer(status))
            self.post(question.channel_id, body.render(result), cards)
        question.write({"state": "answered", "suggest_request": bool(result.get("suggest_request"))})
