"""A link from the panel signs in the person it names, once, for this database, for a minute."""

import base64
import json
import time
import uuid
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from odoo.tests import HttpCase, new_test_user, tagged
from odoo.tools import config

PLATFORM = Ed25519PrivateKey.generate()
PUBLIC = base64.b64encode(PLATFORM.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).decode()


@tagged("post_install", "-at_install")
class TestConnect(HttpCase):
    def setUp(self):
        super().setUp()
        new_test_user(self.env, "ana@acme.pe", email="ana@acme.pe", groups="base.group_user")
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

    def test_a_link_signs_in_the_person_it_names(self):
        response = self.url_open(self.link(), allow_redirects=False)

        self.assertIn(response.status_code, (302, 303))
        self.assertEqual(self.signed_in_as(), "ana@acme.pe")

    def test_a_link_works_once(self):
        link = self.link()
        self.url_open(link, allow_redirects=False)
        self.url_open("/web/session/logout", allow_redirects=False)

        self.assertEqual(self.url_open(link, allow_redirects=False).status_code, 403)

    def test_a_link_that_expired_another_address_or_nobody_is_refused(self):
        for claims in ({"exp": time.time() - 120}, {"host": "elsewhere.example"}, {"email": "nobody@acme.pe"}):
            self.assertEqual(self.url_open(self.link(**claims), allow_redirects=False).status_code, 403, claims)

    def test_without_the_platform_key_it_says_it_is_not_set_up_yet(self):
        with patch.dict(config.options, {"dooservice_connect_key": ""}):
            response = self.url_open(self.link(), allow_redirects=False)

        self.assertEqual(response.status_code, 503)

    def test_a_link_signed_by_anyone_else_is_refused(self):
        response = self.url_open(self.link(signer=Ed25519PrivateKey.generate()), allow_redirects=False)

        self.assertEqual(response.status_code, 403)
