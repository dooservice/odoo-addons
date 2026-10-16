"""The platform, asked from this Odoo's server with the project's key; never from a browser.

The key and the address come from odoo.conf, where the platform writes them. They are
not in the database, so a copy of it carries neither.
"""

import requests

from odoo.tools import config

from ..constants import API_PREFIX, CONFIG_KEY, CONFIG_URL, DEFAULT_URL, TIMEOUT_SECONDS


class BusinessError(Exception):
    """What the platform refused, by its code: `no_ai_account`, `business_disabled`, ..."""

    def __init__(self, code, detail=""):
        super().__init__(detail or code)
        self.code = code


class BusinessClient:
    def __init__(self, key=None, url=None, session=None):
        self.key = key if key is not None else (config.get(CONFIG_KEY) or "")
        self.url = (url or config.get(CONFIG_URL) or DEFAULT_URL).rstrip("/")
        self.session = session or requests

    @property
    def configured(self):
        return bool(self.key)

    def call(self, method, path, body=None, params=None):
        if not self.configured:
            raise BusinessError("business_not_configured")
        try:
            response = self.session.request(
                method,
                f"{self.url}{API_PREFIX}{path}",
                json=body,
                params=params,
                headers={"Authorization": f"Bearer {self.key}"},
                timeout=TIMEOUT_SECONDS,
            )
        except requests.RequestException as error:
            raise BusinessError("business_unreachable", str(error)) from error
        try:
            document = response.json()
        except ValueError:
            document = {}
        if response.status_code >= 400:
            raise BusinessError(str(document.get("code") or response.status_code), str(document.get("detail", "")))
        return document

    def status(self):
        return self.call("GET", "")

    def open_ticket(self, body):
        return self.call("POST", "/tickets", body)

    def messages(self, number, since):
        return self.call("GET", f"/tickets/{number}/messages", params={"since": since} if since else None)

    def send(self, number, body):
        return self.call("POST", f"/tickets/{number}/messages", body)

    def act(self, number, body):
        return self.call("POST", f"/tickets/{number}/act", body)
