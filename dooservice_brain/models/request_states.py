"""The states and kinds of a request, as the platform names them, and following them from it."""

from odoo import _

from ..services.client import AssistantClient, AssistantError

KINDS = [("view", "View"), ("automate", "Automation"), ("build", "Development"), ("adopt", "Taken into a module")]
STATES = [
    ("new", "New"),
    ("draft", "To send"),
    ("queued", "Queued"),
    ("building", "Being built"),
    ("ready", "In review"),
    ("approved", "Approved"),
    ("deployed", "Deployed"),
    ("rejected", "Rejected"),
    ("cancelled", "Cancelled"),
    ("out_of_scope", "With your consultant"),
    ("failed", "Stopped"),
]
FINISHED = ("new", "deployed", "rejected", "cancelled")


class StateFollowing:
    def __init__(self, env, client=None):
        self.env = env
        self.client = client or AssistantClient()

    @staticmethod
    def values_of(remote):
        return {
            "remote_id": remote.get("id"),
            "number": remote.get("number") or 0,
            "name": remote.get("title") or False,
            "summary": remote.get("summary") or False,
            "kind": remote.get("kind") or False,
            "state": remote.get("state") or "draft",
            "model_name": remote.get("model_name") or False,
            "rows": remote.get("rows") or 0,
            "review_comment": remote.get("review_comment") or False,
        }

    def follow(self):
        open_requests = self.env["dooservice.brain.request"].sudo().search(
            [("remote_id", "!=", False), ("state", "not in", FINISHED)]
        )
        if not open_requests or not self.client.configured:
            return
        try:
            remote = {item["id"]: item for item in self.client.requests()}
        except AssistantError:
            return
        for request in open_requests:
            found = remote.get(request.remote_id)
            if found and found.get("state") != request.state:
                request.write(self.values_of(found))
                request.message_post(
                    body=_("This request is now: %(state)s", state=dict(STATES)[request.state]),
                    partner_ids=request.requested_by.partner_id.ids,
                    subtype_xmlid="mail.mt_comment",
                )
