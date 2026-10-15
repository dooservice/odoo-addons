"""The platform, asked from this Odoo's server with the project's key; never from a browser.

The key and the address come from odoo.conf, where the platform writes them. They are
not in the database, so a copy of it carries neither.
"""

import requests

from odoo.tools import config

from ..constants import CONFIG_KEY, CONFIG_URL, DEFAULT_URL, TIMEOUT_SECONDS


class AssistantError(Exception):
    """What the platform refused, by its code: `no_ai_account`, `assistant_not_ready`, ..."""

    def __init__(self, code, detail=""):
        super().__init__(detail or code)
        self.code = code


class AssistantClient:
    def __init__(self, key=None, url=None, session=None):
        self.key = key if key is not None else (config.get(CONFIG_KEY) or "")
        self.url = (url or config.get(CONFIG_URL) or DEFAULT_URL).rstrip("/")
        self.session = session or requests

    @property
    def configured(self):
        return bool(self.key)

    def call(self, method, path, body=None, params=None):
        if not self.configured:
            raise AssistantError("assistant_not_configured")
        try:
            response = self.session.request(
                method,
                f"{self.url}/assistant{path}",
                json=body,
                params=params,
                headers={"Authorization": f"Bearer {self.key}"},
                timeout=TIMEOUT_SECONDS,
            )
        except requests.RequestException as error:
            raise AssistantError("assistant_unreachable", str(error)) from error
        try:
            document = response.json()
        except ValueError:
            document = {}
        if response.status_code >= 400:
            raise AssistantError(str(document.get("code") or response.status_code), str(document.get("detail", "")))
        return document

    def status(self):
        return self.call("GET", "")

    def ask(self, question, screen_model, language, history):
        body = {"question": question, "screen_model": screen_model, "language": language, "history": history}
        return self.call("POST", "/ask", body)

    def understand(self, text, screen_model, language, login, name):
        body = {
            "text": text,
            "screen_model": screen_model,
            "language": language,
            "user_login": login,
            "user_name": name,
        }
        return self.call("POST", "/requests", body)

    def feedback(self, question, rating, name):
        return self.call("POST", "/feedback", {"question": question, "rating": rating, "user_name": name})

    def submit(self, remote_id):
        return self.call("POST", f"/requests/{remote_id}/submit")

    def cancel(self, remote_id):
        return self.call("POST", f"/requests/{remote_id}/cancel")

    def requests(self):
        return self.call("GET", "/requests").get("requests", [])
