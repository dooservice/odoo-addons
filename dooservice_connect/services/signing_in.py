"""Opening a session for the person a link names: the Odoo user whose login or email is theirs.

The same two steps Odoo takes once a second factor is checked: the platform already
checked who this is, and the link was made for them a minute ago.
"""

from odoo.http import request
from odoo.http.session import finalize

from .token import ConnectRefused


class SigningIn:
    def __init__(self, env):
        self.env = env

    def user_of(self, email):
        users = self.env["res.users"].sudo().with_context(active_test=True)
        found = users.search([("login", "=ilike", email), ("share", "=", False)], limit=1)
        found = found or users.search([("email", "=ilike", email), ("share", "=", False)], limit=1)
        if not found:
            raise ConnectRefused("no internal user has this email")
        return found

    def open(self, user):
        request.session["pre_login"] = user.login
        request.session["pre_uid"] = user.id
        finalize(request.session, self.env)
