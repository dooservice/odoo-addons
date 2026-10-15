"""Opening a session as this Odoo's administrator, the way «Connect» does on Odoo.sh.

The panel's account is never the person's Odoo user, so nobody is looked up by email: the
platform already decided who may come in (a developer of the environment, and only a
project admin on production), and the link names them for the log.
"""

from odoo.http import request
from odoo.http.session import finalize

from .token import ConnectRefused


class SigningIn:
    def __init__(self, env):
        self.env = env

    def administrator(self):
        admin = self.env.ref("base.user_admin", raise_if_not_found=False)
        if not admin or not admin.sudo().active:
            raise ConnectRefused("this Odoo has no active administrator")
        return admin.sudo()

    def open(self, user):
        request.session["pre_login"] = user.login
        request.session["pre_uid"] = user.id
        finalize(request.session, self.env)
