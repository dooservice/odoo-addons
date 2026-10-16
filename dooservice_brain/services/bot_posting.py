"""What Dooservice says in a ticket's chat: the platform's messages, posted once each, with their pieces.

Messages the platform returns are posted as the bot; a consultant's or a responsible's reply
carries their name on its first line, and a system message is drawn as a notice. A message
already posted, known by the platform's id, is not posted again.
"""

from markupsafe import Markup, escape

from odoo.tools.mail import plaintext2html

from ..constants import BOT_PARTNER

NAMED_AUTHORS = ("consultant", "responsible")


class BotPosting:
    def __init__(self, env):
        self.env = env
        self.bot = env.ref(BOT_PARTNER)

    def post(self, channel, body, cards=None, remote_id=0, system=False):
        message = (
            channel.sudo()
            .with_context(dooservice_bot=True)
            .message_post(
                author_id=self.bot.id,
                body=body,
                message_type="notification" if system else "comment",
                silent=True,
                subtype_xmlid="mail.mt_comment",
            )
        )
        values = {}
        if cards:
            values["dooservice_cards"] = [
                {**card, "id": card.get("id") or f"c{index}"} for index, card in enumerate(cards)
            ]
        if remote_id:
            values["dooservice_remote_id"] = int(remote_id)
        if values:
            message.sudo().write(values)
        return message

    def notice(self, channel, text):
        return self.post(channel, Markup('<div class="o_mail_notification">%s</div>') % text, system=True)

    def remote(self, ticket, messages):
        """The platform's messages for a ticket, in order; what people wrote here is already in the chat."""
        posted = []
        for item in messages:
            if item.get("author") == "user" or self.known(ticket, item.get("id")):
                continue
            if item.get("author") == "system":
                posted.append(
                    self.post(ticket.channel_id, self.notice_body(item), remote_id=item.get("id"), system=True)
                )
            else:
                posted.append(self.post(ticket.channel_id, self.body(item), item.get("cards") or [], item.get("id")))
        return posted

    def known(self, ticket, remote_id):
        if not remote_id:
            return False
        return bool(
            self.env["mail.message"]
            .sudo()
            .search_count(
                [
                    ("model", "=", "discuss.channel"),
                    ("res_id", "=", ticket.channel_id.id),
                    ("dooservice_remote_id", "=", int(remote_id)),
                ],
                limit=1,
            )
        )

    def body(self, item):
        text = plaintext2html(item.get("text") or "")
        if item.get("author") in NAMED_AUTHORS and item.get("author_name"):
            return Markup("<b>%s</b>") % item["author_name"] + text
        return text

    def notice_body(self, item):
        return Markup('<div class="o_mail_notification">%s</div>') % escape(item.get("text") or "")
