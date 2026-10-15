"""A draft sent from the chat: a request the person follows here, or one asked of an administrator.

Someone who may request changes sends it straight away. Someone who may only ask leaves it
with the administrators, who read it and send it, or not.
"""

from odoo import _
from odoo.exceptions import UserError

from ..constants import GROUP_REQUEST, GROUP_SYSTEM
from .client import AssistantError
from .request_states import KINDS, StateFollowing
from .wording import Wording


class DraftSending:
    def __init__(self, env, client):
        self.env = env
        self.client = client

    def send(self, message, card):
        user = self.env.user
        request = (
            self.env["dooservice.brain.request"]
            .sudo()
            .create(
                {
                    "text": card.get("text") or "",
                    "name": card.get("title") or False,
                    "summary": card.get("summary") or False,
                    "kind": card.get("kind") if card.get("kind") in dict(KINDS) else False,
                    "model_name": card.get("model") or False,
                    "rows": card.get("rows") or 0,
                    "remote_id": card.get("remote_id") or False,
                    "state": "draft" if card.get("remote_id") else "new",
                    "requested_by": user.id,
                    "message_id": message.id,
                }
            )
        )
        if not user.has_group(GROUP_REQUEST):
            self.ask_administrators(request)
            return {"done": "asked", "request": request.id}
        if not request.remote_id:
            raise UserError(Wording.refusal(card.get("unavailable") or "", user.lang or ""))
        try:
            request.write(StateFollowing.values_of(self.client.submit(request.remote_id)))
        except AssistantError as error:
            raise UserError(Wording.refusal(error.code, user.lang or "")) from error
        return {"done": "send", "request": request.id}

    def ask_administrators(self, request):
        administrators = self.env.ref(GROUP_REQUEST).users.filtered(
            lambda person: person.has_group(GROUP_SYSTEM)
        )
        partners = (administrators - self.env.user).partner_id
        request.message_subscribe(partner_ids=partners.ids)
        request.message_post(
            body=_("%(name)s asks for this from the assistant's chat.", name=self.env.user.name),
            partner_ids=partners.ids,
            subtype_xmlid="mail.mt_comment",
        )

    def cancel(self, card):
        """A draft nobody sends is forgotten by the platform within a day; cancelling only says so sooner."""
        if card.get("remote_id"):
            try:
                self.client.cancel(card["remote_id"])
            except AssistantError:
                return

    def cancel_request(self, request_id):
        request = self.env["dooservice.brain.request"].sudo().browse(request_id).exists()
        if not request or request.requested_by != self.env.user:
            raise UserError(_("This request is not yours."))
        if not request.remote_id:
            request.state = "cancelled"
            return
        try:
            request.write(StateFollowing.values_of(self.client.cancel(request.remote_id)))
        except AssistantError as error:
            raise UserError(Wording.refusal(error.code, self.env.user.lang or "")) from error
