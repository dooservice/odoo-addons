"""An answer as it is posted in the chat: its text, and the line saying who answered."""

from markupsafe import escape


class AnswerBody:
    def __init__(self, env):
        self.env = env

    def render(self, result):
        """The text alone: its sources, the model and what it proposes go in its pieces."""
        return escape(result.get("answer") or "")

    def footer(self, status):
        if not status.get("model_label"):
            return self.env._("No record of this Odoo is sent.")
        owner = (
            self.env._("this project's own account")
            if status.get("account_scope") == "project"
            else self.env._("the account of %(name)s", name=status.get("organization_name") or "")
        )
        return self.env._(
            "%(model)s · %(owner)s. No record of this Odoo is sent.", model=status["model_label"], owner=owner
        )

    def unreviewed(self):
        return self.env._("Nobody has reviewed how this works yet, so I would rather not guess.")
