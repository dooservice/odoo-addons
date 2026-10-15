"""What the assistant tells a person when the platform could not answer, in their language."""

from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate("dooservice_brain")


class Wording:
    refusals = {
        "assistant_not_configured": _lt("The assistant is not set up on this database yet. Ask your consultant."),
        "assistant_key_invalid": _lt("The assistant's key is no longer valid. Ask your consultant to set it again."),
        "assistant_not_ready": _lt("The server of this Odoo needs an update before the assistant can answer."),
        "assistant_unreachable": _lt("The assistant could not be reached. Try again in a few minutes."),
        "no_ai_account": _lt("No AI account is set for this project, so the assistant cannot answer."),
        "ai_limit_reached": _lt("The AI account reached its limit for this month. Ask your consultant."),
        "assistant_requests_off": _lt("Requests are not turned on for this project. Ask your consultant."),
        "assistant_no_repository": _lt("This project has no repository yet, so requests cannot be built."),
        "brain_request_state": _lt("This request cannot be changed that way any more."),
        "assistant_on_hold": _lt("The assistant is paused while this project's plan is on hold. Ask your consultant."),
    }
    fallback = _lt("The assistant could not answer this time. Try again later.")

    @classmethod
    def refusal(cls, code, lang=""):
        return cls.refusals.get(code, cls.fallback)._translate(lang)
