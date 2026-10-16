"""The people of every test: one who may ask, one who may request changes, one responsible, one outside."""

from odoo.tests import TransactionCase, new_test_user

from odoo.addons.dooservice_brain.services.ticket_opening import TicketOpening

from .platform import FakePlatform


class TicketCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bot = cls.env.ref("dooservice_brain.partner_dooservice")
        cls.eva = new_test_user(cls.env, "eva", groups="base.group_user,dooservice_brain.group_ask")
        cls.ana = new_test_user(cls.env, "ana", groups="base.group_user,dooservice_brain.group_request")
        cls.rosa = new_test_user(cls.env, "rosa", groups="base.group_user,dooservice_brain.group_responsible")
        cls.luis = new_test_user(cls.env, "luis", groups="base.group_user")
        cls.record = cls.env["res.partner"].create({"name": "Comercial Los Andes"})

    def opened(self, user, platform=None, kind="incident", text="Why was the advance not deducted?", continues=None):
        platform = platform or FakePlatform()
        env = self.env(user=user)
        return TicketOpening(env, platform).open(kind, text, "res.partner", self.record.id, continues), platform

    def said(self, channel, limit=1):
        return self.env["mail.message"].search(
            [("model", "=", "mail.channel"), ("res_id", "=", channel.id)], limit=limit
        )

    def say(self, user, channel, text):
        return channel.with_user(user).message_post(body=text, message_type="comment", subtype_xmlid="mail.mt_comment")
