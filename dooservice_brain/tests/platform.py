"""The platform as the tests answer it: what was asked is kept, the answers are scripted.

Without a script, a ticket is opened with the next number and one answer of the assistant,
and every other route answers nothing new.
"""

import itertools

from odoo.addons.dooservice_brain.services.client import BusinessError

STATUS = {
    "enabled": True,
    "processes_reviewed": 3,
    "support_hours": {"weekdays": [1, 2, 3, 4, 5], "start": "09:00", "end": "18:00", "timezone": "America/Lima"},
    "response_hours": 4,
    "consultancy_name": "Nexo Consultores",
}
ANSWER = {"id": 101, "author": "assistant", "author_name": "Dooservice", "text": "Here is how it works.", "cards": []}


class FakePlatform:
    def __init__(self, answers=None, refusal=""):
        self.answers = answers or {}
        self.refusal = refusal
        self.asked = []
        self.configured = True
        self.numbers = itertools.count(1)

    def reply(self, name, *args):
        self.asked.append((name, args))
        if self.refusal:
            raise BusinessError(self.refusal)
        answer = self.answers.get(name)
        return answer(*args) if callable(answer) else answer

    def status(self):
        return self.reply("status") or STATUS

    def open_ticket(self, body):
        answer = self.reply("open_ticket", body)
        if answer is not None:
            return answer
        number = next(self.numbers)
        ticket = {
            "number": number,
            "kind": body["kind"],
            "state": "open",
            "title": body["text"][:30],
            "process_name": "Wholesale",
        }
        return {"ticket": ticket, "messages": [ANSWER]}

    def messages(self, number, since):
        return self.reply("messages", number, since) or {"ticket": {}, "messages": []}

    def send(self, number, body):
        return self.reply("send", number, body) or {"ticket": {}, "messages": []}

    def act(self, number, body):
        return self.reply("act", number, body) or {"ticket": {}, "messages": []}

    def names(self):
        return [name for name, _args in self.asked]


REPLY = {
    "id": 202,
    "author": "assistant",
    "text": "Because it was created from Invoicing.",
    "cards": [{"type": "resolved", "title": "Was it resolved?"}],
}
ESCALATED = {
    "ticket": {"number": 1, "state": "waiting_consultant", "deadline_at": "2026-10-16T18:00:00Z"},
    "messages": [
        {"id": 303, "author": "consultant", "author_name": "Julia Soto", "text": "Never cancel a posted invoice."}
    ],
}
FOR_RESPONSIBLE = {"ticket": {"number": 1, "state": "waiting_user", "waiting_for": "responsible"}, "messages": []}
RESOLVED = {
    "id": 202,
    "author": "assistant",
    "text": "Because it was created from Invoicing.",
    "cards": [{"type": "resolved"}],
}
APPROVAL = {
    "id": 203,
    "author": "assistant",
    "text": "Waiting for the approval of your responsible.",
    "cards": [{"type": "approval"}],
}
CLOSED = {
    "ticket": {"number": 1, "state": "closed"},
    "messages": [{"id": 404, "author": "system", "text": "Ticket closed by Ana"}],
}
