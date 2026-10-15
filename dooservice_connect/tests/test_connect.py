"""A link from the panel signs in as the administrator, once, for this database, for a minute."""

import base64
import json
import time
import uuid
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from odoo.tests import HttpCase, tagged
from odoo.tools import config

PLATFORM = Ed25519PrivateKey.generate()
PUBLIC = base64.b64encode(PLATFORM.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).decode()


@tagged("post_install", "-at_install")
class TestConnect(HttpCase):
    def setUp(self):
        super().setUp()
        self.patcher = patch.dict(config.options, {"dooservice_connect_key": PUBLIC})
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def link(self, signer=PLATFORM, **claims):
        host = self.base_url().split("://", 1)[1]
        body = {"host": host, "email": "ana@acme.pe", "exp": time.time() + 60, "nonce": uuid.uuid4().hex}
        body.update(claims)
        encoded = base64.urlsafe_b64encode(json.dumps(body).encode()).decode().rstrip("=")
        signature = base64.urlsafe_b64encode(signer.sign(encoded.encode())).decode().rstrip("=")
        return f"/_dooservice/connect?token={encoded}.{signature}"

    def signed_in_as(self):
        info = self.url_open("/web/session/get_session_info", data=json.dumps({}), headers={"Content-Type": "application/json"})
        return (info.json().get("result") or {}).get("username")

    def assertSentToLogin(self, response, why=None):
        self.assertIn(response.status_code, (302, 303), why)
        self.assertTrue(response.headers["Location"].endswith("/web/login"), why)

    def test_a_link_signs_in_as_the_administrator_whoever_it_names(self):
        response = self.url_open(self.link(), allow_redirects=False)

        self.assertIn(response.status_code, (302, 303))
        self.assertEqual(self.signed_in_as(), self.env.ref("base.user_admin").login)

    def test_a_link_works_once(self):
        link = self.link()
        self.url_open(link, allow_redirects=False)
        self.url_open("/web/session/logout", allow_redirects=False)

        self.assertSentToLogin(self.url_open(link, allow_redirects=False))

    def test_a_link_that_expired_for_another_address_or_naming_nobody_is_refused(self):
        for claims in ({"exp": time.time() - 120}, {"host": "elsewhere.example"}, {"email": ""}):
            self.assertSentToLogin(self.url_open(self.link(**claims), allow_redirects=False), claims)

    def test_without_the_platform_key_it_goes_to_the_login(self):
        with patch.dict(config.options, {"dooservice_connect_key": ""}):
            response = self.url_open(self.link(), allow_redirects=False)

        self.assertSentToLogin(response)

    def test_a_link_signed_by_anyone_else_is_refused(self):
        response = self.url_open(self.link(signer=Ed25519PrivateKey.generate()), allow_redirects=False)

        self.assertSentToLogin(response)
