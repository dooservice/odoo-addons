"""The platform as the tests answer it: what was asked is kept, the answers are scripted."""

from odoo.addons.dooservice_brain.services.client import AssistantError

STATUS = {"model_label": "Claude Haiku 5.5", "account_scope": "organization", "organization_name": "Consultora Andina"}


class FakePlatform:
    def __init__(self, answers=None, refusal=""):
        self.answers = answers or {}
        self.refusal = refusal
        self.asked = []
        self.configured = True

    def reply(self, name, *args):
        self.asked.append((name, args))
        if self.refusal:
            raise AssistantError(self.refusal)
        return self.answers.get(name, {})

    def status(self):
        return STATUS

    def ask(self, *args):
        return self.reply("ask", *args)

    def understand(self, *args):
        return self.reply("understand", *args)

    def feedback(self, *args):
        return self.reply("feedback", *args)

    def submit(self, *args):
        return self.reply("submit", *args)

    def cancel(self, *args):
        return self.reply("cancel", *args)

    def requests(self):
        return self.reply("requests").get("requests", [])
