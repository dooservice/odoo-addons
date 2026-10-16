"""What Dooservice tells a person when the platform could not take a ticket or a message, in their language."""

from odoo import _lt
from odoo.tools.translate import code_translations


class Wording:
    refusals = {
        "business_not_configured": _lt("Dooservice is not set up on this database yet. Ask your consultancy."),
        "business_key_invalid": _lt("The key of this Odoo is no longer valid. Ask your consultancy to set it again."),
        "business_not_ready": _lt("The server of this Odoo needs an update before Dooservice can answer."),
        "business_unreachable": _lt("Dooservice could not be reached. Try again in a few minutes."),
        "business_disabled": _lt("Tickets are not turned on for this project. Ask your consultancy."),
        "business_on_hold": _lt("Dooservice is paused while this project's plan is on hold. Ask your consultancy."),
        "no_ai_account": _lt("No AI account is set for this project, so Dooservice cannot answer."),
        "ai_limit_reached": _lt("The AI account reached its limit for this month. Ask your consultancy."),
        "ticket_not_found": _lt("This ticket is no longer known to Dooservice."),
        "ticket_closed": _lt("This ticket is closed. To continue, open a new one linked to it."),
        "card_done": _lt("This was already answered."),
    }
    fallback = _lt("Dooservice could not take this right now. Try again later.")

    @classmethod
    def refusal(cls, code, lang=""):
        return cls.translated(cls.refusals.get(code, cls.fallback), lang)

    @classmethod
    def translated(cls, lazy, lang=""):
        """A lazy text in the given language: Odoo 17 keeps the module's translations by source."""
        translations = code_translations.get_python_translations("dooservice_brain", lang or "en_US")
        return translations.get(lazy._source, lazy._source)
