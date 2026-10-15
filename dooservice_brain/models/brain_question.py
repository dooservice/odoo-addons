"""A question posted to Dooservice in a chat, answered by a scheduled task so nobody waits on it.

Posting returns at once; the task is triggered to run now and posts the answer as
Dooservice in the same chat. The question and its answer stay in this database only.
"""

from odoo import api, fields, models
from odoo.tools import html2plaintext

from ..constants import ANSWER_CRON, BOT_PARTNER, GROUP_ASK, QUESTION_MAX_CHARACTERS, QUESTIONS_PER_RUN
from ..services.answering import Answering


class BrainQuestion(models.Model):
    _name = "dooservice.brain.question"
    _description = "Question to the Dooservice assistant"
    _order = "id desc"

    channel_id = fields.Many2one("discuss.channel", required=True, ondelete="cascade", index=True)
    message_id = fields.Many2one("mail.message", ondelete="set null")
    user_id = fields.Many2one("res.users", required=True, ondelete="cascade", index=True)
    text = fields.Text(required=True)
    screen_model = fields.Char()
    state = fields.Selection(
        [("pending", "Pending"), ("answered", "Answered"), ("failed", "Failed")],
        default="pending",
        required=True,
        index=True,
    )
    suggest_request = fields.Boolean()
    error = fields.Char()

    @api.model
    def _receive(self, channel, message):
        bot = self.env.ref(BOT_PARTNER, raise_if_not_found=False)
        if not bot or channel.channel_type != "chat" or message.message_type != "comment":
            return
        if message.author_id == bot or bot not in channel.channel_member_ids.partner_id:
            return
        user = message.author_id.user_ids[:1]
        text = html2plaintext(message.body or "").strip()[:QUESTION_MAX_CHARACTERS]
        if not user or not text:
            return
        if not user.has_group(GROUP_ASK):
            Answering(self.env).post(channel, self.env._("You do not have access to the assistant. Ask your administrator."))
            return
        self.sudo().create(
            {
                "channel_id": channel.id,
                "message_id": message.id,
                "user_id": user.id,
                "text": text,
                "screen_model": user.dooservice_brain_screen or False,
            }
        )
        self.env.ref(ANSWER_CRON).sudo()._trigger()

    @api.model
    def _answer_pending(self):
        for question in self.sudo().search([("state", "=", "pending")], order="id", limit=QUESTIONS_PER_RUN):
            Answering(self.env).answer(question)
            self.env.cr.commit()
