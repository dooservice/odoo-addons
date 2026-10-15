"""What the browser draws under an answer: its pieces, what was done with them, and how sent requests go."""

from odoo.exceptions import AccessError

from ..constants import FINISHED_REQUEST_STATES, GROUP_REQUEST
from .card_guard import CardGuard


class CardPayload:
    def __init__(self, env):
        self.env = env

    def of(self, message_ids):
        found = {}
        for message_id in message_ids:
            try:
                message = CardGuard(self.env).message(message_id)[0]
            except AccessError:
                continue
            found[message.id] = self.one(message)
        return found

    def one(self, message):
        state = message.dooservice_card_state or {}
        requests = (
            self.env["dooservice.brain.request"]
            .sudo()
            .browse([done["request"] for done in state.values() if done.get("request")])
            .exists()
        )
        labels = dict(requests._fields["state"]._description_selection(self.env))
        return {
            "cards": message.dooservice_cards,
            "state": state,
            "can_request": self.env.user.has_group(GROUP_REQUEST),
            "requests": {
                request.id: {
                    "state": request.state,
                    "label": labels.get(request.state, request.state),
                    "number": request.number,
                    "finished": request.state in FINISHED_REQUEST_STATES,
                }
                for request in requests
            },
        }
