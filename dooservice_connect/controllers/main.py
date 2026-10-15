import logging

from odoo import http
from odoo.http import request

from ..constants import LANDING, NOT_READY, REFUSED
from ..services.signing_in import SigningIn
from ..services.token import ConnectNotReady, ConnectRefused, ConnectToken
from ..services.used import UsedLinks

_logger = logging.getLogger(__name__)


class ConnectController(http.Controller):
    @http.route("/_dooservice/connect", type="http", auth="none", methods=["GET"], csrf=False)
    def connect(self, token=None):
        """From «Connect» in the panel: signed in as yourself, or told that it did not work."""
        try:
            claims = ConnectToken.claims(token, request.httprequest.host)
            UsedLinks().take(str(claims["nonce"]))
            signing_in = SigningIn(request.env)
            signing_in.open(signing_in.user_of(str(claims["email"])))
        except ConnectNotReady:
            _logger.warning("Dooservice Connect has no platform key yet; Odoo reads it when it restarts")
            return request.make_response(NOT_READY, status=503)
        except ConnectRefused as refused:
            _logger.warning("Dooservice Connect refused a link: %s", refused)
            return request.make_response(REFUSED, status=403)
        return request.redirect(LANDING)
