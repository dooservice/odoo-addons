"""An answer as it is posted in the chat: its text, and the line saying who answered."""

from odoo import _
from markupsafe import escape


class AnswerBody:
    def __init__(self, env):
        self.env = env

    def render(self, result):
        """The text alone: its sources, the model and what it proposes go in its pieces."""
        return escape(result.get("answer") or "")

    def footer(self, status):
        if not status.get("model_label"):
            return _("No record of this Odoo is sent.")
        owner = (
            _("this project's own account")
            if status.get("account_scope") == "project"
            else _("the account of %(name)s", name=status.get("organization_name") or "")
        )
        return _(
            "%(model)s · %(owner)s. No record of this Odoo is sent.", model=status["model_label"], owner=owner
        )

    def unreviewed(self):
        return _("Nobody has reviewed how this works yet, so I would rather not guess.")
