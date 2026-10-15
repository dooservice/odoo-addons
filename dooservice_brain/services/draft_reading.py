"""A draft request read back by the platform: what it understood, ready for the person to send.

The platform keeps it as a draft nobody else sees and forgets it within a day unless it is
sent; reading it again after a correction replaces it.
"""

from .client import AssistantError


class DraftReading:
    def __init__(self, client):
        self.client = client

    def read(self, user, text, screen_model, title=""):
        try:
            read = self.client.understand(text, screen_model or "", (user.lang or "en")[:2], user.login, user.name)
        except AssistantError as error:
            return {"text": text, "title": title, "unavailable": error.code}
        return {
            "text": text,
            "title": read.get("title") or title or "",
            "summary": read.get("summary") or "",
            "kind": read.get("kind") or "",
            "model": read.get("model_name") or "",
            "rows": read.get("rows") or 0,
            "remote_id": read.get("id") or "",
        }
