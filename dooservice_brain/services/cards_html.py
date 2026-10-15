"""Odoo 16 draws no pieces in the browser: they are written in the answer itself, as signed links.

Each link does one thing for the person whose chat it is; once done, the answer is written
again saying what was done.
"""

from urllib.parse import urlencode

from markupsafe import Markup

from odoo import _
from odoo.tools.misc import hmac

from ..constants import BOT_PARTNER
from .chart_counting import ChartCounting

MARK = '<div class="o_dooservice_cards">'
SCOPE = "dooservice_brain.card"
RATED = {"up": "👍", "down": "👎"}


class CardsHtml:
    def __init__(self, env):
        self.env = env

    @classmethod
    def token(cls, env, uid, message_id, card_id, action, value):
        return hmac(env(su=True), SCOPE, f"{uid}:{message_id}:{card_id}:{action}:{value}")

    def refresh(self, message):
        channel = self.env[message.model].sudo().browse(message.res_id)
        self.person = (channel.channel_member_ids.partner_id - self.env.ref(BOT_PARTNER)).user_ids[:1]
        self.message = message
        state = message.dooservice_card_state or {}
        parts = [self.card(card, state.get(card["id"]) or {}) for card in message.dooservice_cards or []]
        text = str(message.body or "").split(MARK)[0]
        message.sudo().body = Markup(text) + Markup(MARK) + Markup("").join(parts) + Markup("</div>")

    def link(self, card, action, label, value=""):
        token = self.token(self.env, self.person.id, self.message.id, card["id"], action, value)
        query = urlencode({"value": value, "token": token})
        url = f"/dooservice_brain/card/{self.message.id}/{card['id']}/{action}?{query}"
        return Markup('<a class="btn btn-sm btn-secondary me-1" href="%s">%s</a>') % (url, label)

    def card(self, card, done):
        kind = card.get("type")
        title = Markup("<b>%s</b><br/>") % card["title"] if card.get("title") else Markup("")
        if kind == "sources":
            return Markup("<p><small>%s</small></p>") % " · ".join(card["items"])
        if kind == "meta":
            return Markup('<p><small class="text-muted">%s</small></p>') % card["text"]
        if done.get("done") and kind != "draft":
            return Markup("<p>%s✓ %s</p>") % (title, RATED.get(done.get("value"), done.get("value")) or _("Done"))
        if kind in ("choice", "multi"):
            return Markup("<p>%s%s</p>") % (
                title,
                Markup("").join(self.link(card, "choose", o["label"], o["value"]) for o in card["options"]),
            )
        if kind == "field":
            return Markup("<p>%s<small>%s</small></p>") % (title, _("Answer in the chat."))
        if kind == "draft":
            return self.draft(card, done, title)
        if kind == "flow":
            return Markup("<p>%s%s</p>") % (
                title,
                " → ".join(f"{i + 1}. {s['title']}" for i, s in enumerate(card["steps"])),
            )
        if kind == "chart":
            counted = ChartCounting(self.env(user=self.person)).count(card)
            lines = [f"{g['label']}: {g['count']}" for g in counted.get("groups", [])] or [_("Nothing to count.")]
            return Markup("<p>%s%s</p>") % (title, Markup("<br/>").join(lines))
        if kind == "table":
            head = Markup("").join(Markup("<th>%s</th>") % c for c in card["columns"])
            rows = Markup("").join(
                Markup("<tr>%s</tr>") % Markup("").join(Markup("<td>%s</td>") % c for c in r) for r in card["rows"]
            )
            return Markup('%s<table class="table table-sm"><tr>%s</tr>%s</table>') % (title, head, rows)
        if kind == "feedback":
            return Markup("<p>%s%s</p>") % (self.link(card, "rate", "👍", "up"), self.link(card, "rate", "👎", "down"))
        if kind == "error":
            return Markup("<p>%s</p>") % self.link(card, "retry", _("Retry"))
        return Markup("")

    def draft(self, card, done, title):
        body = Markup("%s%s") % (title, card.get("summary") or card.get("text") or "")
        if done.get("request"):
            request = self.env["dooservice.brain.request"].sudo().browse(done["request"])
            label = dict(request._fields["state"]._description_selection(self.env)).get(request.state)
            return Markup("<p>%s<br/><small>#%s · %s</small></p>") % (body, request.number, label)
        if done.get("done") == "cancel":
            return Markup("<p>%s<br/><small>%s</small></p>") % (body, _("Cancelled: nothing was created."))
        send = _("Send") if self.person.has_group("dooservice_brain.group_request") else _("Ask an administrator")
        links = (self.link(card, "send", send) if not card.get("unavailable") else Markup("")) + self.link(
            card, "cancel", _("Cancel")
        )
        return Markup("<p>%s<br/>%s</p>") % (body, links)
