"""Odoo 16 draws no pieces in the browser: they are written in the message itself, as signed links.

Each link does one thing, once, for a member of the ticket's chat; after it the message is
written again saying what was done. A correction needs words, so it is asked for in the chat.
"""

from urllib.parse import urlencode

from markupsafe import Markup

from odoo import _lt
from odoo.tools.misc import hmac

from ..constants import CARD_ACTIONS, CLOSED_STATES, CONTINUE_CARD, NEW_TICKET_ACTION
from .wording import Wording

MARK = '<div class="o_dooservice_cards">'
SCOPE = "dooservice_brain.card"
OPTIONS = {
    "resolved": (("yes", _lt("Yes, close")), ("no", _lt("No, continue"))),
    "understood": (("yes", _lt("Yes, it is correct")), ("cancel", _lt("Cancel"))),
    "approval": (("approve", _lt("Approve")), ("decline", _lt("Decline"))),
    "rating": (("up", _lt("👍")), ("down", _lt("👎"))),
}
NEEDS_WORDS = _lt("To correct it, write what should change in the chat.")
CONTINUE = _lt("Open a new linked ticket")
#: What a piece says before its buttons, in the order it is read; the items are joined.
HEAD = (
    ("title", Markup("<b>%s</b>")),
    ("text", Markup("%s")),
    ("items", Markup("<small>%s</small>")),
    ("footer", Markup('<small class="text-muted">%s</small>')),
)


class CardsHtml:
    def __init__(self, env):
        self.env = env

    @classmethod
    def token(cls, env, message_id, card_id, action, value, label):
        return hmac(env(su=True), SCOPE, f"{message_id}:{card_id}:{action}:{value}:{label}")

    def refresh(self, message):
        """The pieces written again under the text, and the chat told of the new body."""
        ticket = self.env["dooservice.ticket"].sudo().search([("channel_id", "=", message.res_id)], limit=1)
        self.message, self.lang, state = message, ticket.user_id.lang or "", message.dooservice_card_state or {}
        parts = [self.card(card, state.get(card["id"]) or {}, ticket) for card in message.dooservice_cards or []]
        text = str(message.body or "").split(MARK)[0]
        message.sudo().body = Markup(text) + Markup(MARK) + Markup("").join(parts) + Markup("</div>")
        channel = self.env[message.model].sudo().browse(message.res_id)
        self.env["bus.bus"]._sendone(channel, "mail.message/insert", {"id": message.id, "body": message.body})

    def card(self, card, done, ticket):
        kind, lines = card.get("type"), self.head(card)
        if kind == CONTINUE_CARD:
            lines.append(self.continue_link(card))
        elif done.get("done"):
            lines.append(Markup("✓ %s") % self.said(card, done))
        elif kind in CARD_ACTIONS and ticket.state not in CLOSED_STATES:
            lines.append(self.links(card))
        return Markup("<p>%s</p>") % Markup("<br/>").join(lines)

    def head(self, card):
        said = {key: " · ".join(card[key]) if key == "items" else card[key] for key, _shape in HEAD if card.get(key)}
        return [shape % said[key] for key, shape in HEAD if key in said]

    def options(self, card):
        """What the platform offers for the piece, or what its kind offers by default; typed answers go to the chat."""
        given = [(o["value"], o.get("label") or o["value"], bool(o.get("input"))) for o in card.get("options") or []]
        defaults = OPTIONS.get(card["type"], ())
        return given or [(value, Wording.translated(label, self.lang), False) for value, label in defaults]

    def links(self, card):
        options = self.options(card)
        parts = []
        for value, label, needs_words in options:
            if not needs_words:
                action, sent = ("rate", value) if card["type"] == "rating" else (value, "")
                parts.append(self.link(card, action, label, sent))
        if card["type"] == "understood" or any(needs for _value, _label, needs in options):
            parts.append(Markup("<small>%s</small>") % Wording.translated(NEEDS_WORDS, self.lang))
        return Markup(" ").join(parts)

    def said(self, card, done):
        chosen = done["value"] if card["type"] == "rating" else done["done"]
        label = next((label for value, label, _needs in self.options(card) if value == chosen), chosen)
        return f"{label}: {done['value']}" if done.get("value") and card["type"] != "rating" else label

    def link(self, card, action, label, value=""):
        token = self.token(self.env, self.message.id, card["id"], action, value, label)
        query = urlencode({"value": value, "label": label, "token": token})
        url = f"/dooservice_brain/card/{self.message.id}/{card['id']}/{action}?{query}"
        return Markup('<a class="btn btn-sm btn-secondary me-1" href="%s">%s</a>') % (url, label)

    def continue_link(self, card):
        wanted = {"action": NEW_TICKET_ACTION, "continues": card["ticket"], "continues_number": card["number"]}
        query = urlencode(wanted)
        label = Wording.translated(CONTINUE, self.lang)
        return Markup('<a class="btn btn-sm btn-primary" href="/web#%s">%s</a>') % (query, label)
