"""A link from the panel: what it says, and whether the platform signed it, for this database, now.

`<claims>.<signature>`, both base64url: the claims are JSON with the host the link was made
for, the person's email, a one-time `nonce` and `exp`. Only the platform holds the private key; this Odoo has
the public one in odoo.conf, so nobody who reads the database, the file or a backup can
make a link.
"""

import base64
import json
import time

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from odoo.tools import config

from ..constants import CONFIG_KEY, LEEWAY_SECONDS


class ConnectRefused(Exception):
    """Why a link does not sign anybody in; said to nobody but the log."""


class ConnectNotReady(ConnectRefused):
    """This Odoo has no platform key yet: it reads odoo.conf when it starts."""


class ConnectToken:
    @staticmethod
    def decoded(part):
        return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))

    @classmethod
    def claims(cls, token, host):
        key = config.get(CONFIG_KEY) or ""
        if not key:
            raise ConnectNotReady("this Odoo has no platform key")
        claims_part, _, signature_part = (token or "").partition(".")
        if not claims_part or not signature_part:
            raise ConnectRefused("not a link from the platform")
        try:
            Ed25519PublicKey.from_public_bytes(base64.b64decode(key)).verify(
                cls.decoded(signature_part), claims_part.encode()
            )
            claims = json.loads(cls.decoded(claims_part))
        except (InvalidSignature, ValueError) as error:
            raise ConnectRefused("the signature does not hold") from error
        if str(claims.get("host") or "").lower() != (host or "").lower():
            raise ConnectRefused("the link is for another address")
        if float(claims.get("exp") or 0) + LEEWAY_SECONDS < time.time():
            raise ConnectRefused("the link expired")
        if not claims.get("email") or not claims.get("nonce"):
            raise ConnectRefused("the link names nobody")
        return claims
