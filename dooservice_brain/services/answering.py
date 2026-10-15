"""One question answered: the platform asked, the answer posted in the chat as Dooservice."""

from ..constants import BOT_PARTNER, HISTORY_TURNS
from .answer_body import AnswerBody
from .client import AssistantClient, AssistantError
from .status_cache import StatusCache
from .wording import Wording


class Answering:
    def __init__(self, env, client=None):
        self.env = env
        self.client = client or AssistantClient()
        self.bot = env.ref(BOT_PARTNER)

    def post(self, channel, body):
        channel.sudo().message_post(
            author_id=self.bot.id, body=body, message_type="comment", silent=True, subtype_xmlid="mail.mt_comment"
        )

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
            self.post(question.channel_id, Wording.refusal(error.code, lang))
            question.write({"state": "failed", "error": error.code})
            return
        if not result.get("called"):
            self.post(question.channel_id, body.unreviewed())
        else:
            url = f"/dooservice_brain/request/{question.id}" if result.get("suggest_request") else ""
            self.post(question.channel_id, body.render(result, status, url))
        question.write({"state": "answered", "suggest_request": bool(result.get("suggest_request"))})
