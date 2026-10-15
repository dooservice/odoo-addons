"""An answer as it is posted in the chat: the text, the steps it stands on, and who answered."""

from markupsafe import Markup, escape

from odoo import _


class AnswerBody:
    def __init__(self, env):
        self.env = env

    def render(self, result, status, request_url=""):
        parts = [escape(result.get("answer") or "")]
        sources = result.get("sources") or []
        if sources:
            cited = ", ".join(
                _("%(process)s · step %(step)s", process=source.get("name"), step=source.get("step"))
                for source in sources
            )
            parts.append(Markup("<br/><small>%s %s</small>") % (_("Sources:"), cited))
        if request_url:
            link = Markup('<a href="%s">%s</a>') % (request_url, _("Request it"))
            parts.append(Markup("<br/>%s %s") % (_("This does not exist yet."), link))
        parts.append(Markup("<br/><small class='text-muted'>%s</small>") % self.footer(status))
        return Markup("").join(parts)

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
