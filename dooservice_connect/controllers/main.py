import logging

from odoo import http
from odoo.http import request

from ..constants import LANDING, SIGN_IN
from ..services.signing_in import SigningIn
from ..services.token import ConnectNotReady, ConnectRefused, ConnectToken
from ..services.used import UsedLinks

_logger = logging.getLogger(__name__)


class ConnectController(http.Controller):
    @http.route("/_dooservice/connect", type="http", auth="none", methods=["GET"], csrf=False)
    def connect(self, token=None):
        """From «Open instance» in the panel: signed in as the administrator, or at Odoo's login when that cannot be."""
        try:
            claims = ConnectToken.claims(token, request.httprequest.host)
            UsedLinks().take(str(claims["nonce"]))
            signing_in = SigningIn(request.env)
            admin = signing_in.administrator()
            signing_in.open(admin)
            _logger.info("Dooservice Connect: %s signed in as %s", claims["email"], admin.login)
        except ConnectNotReady:
            _logger.warning("Dooservice Connect has no platform key yet; Odoo reads it when it restarts")
            return request.redirect(SIGN_IN)
        except ConnectRefused as refused:
            _logger.warning("Dooservice Connect refused a link: %s", refused)
            return request.redirect(SIGN_IN)
        return request.redirect(LANDING)
