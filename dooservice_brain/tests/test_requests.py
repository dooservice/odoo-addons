"""A request is read back, sent, and followed from the platform, with each change in its chatter."""

from unittest.mock import patch

from odoo.tests import TransactionCase, new_test_user, tagged

from odoo.addons.dooservice_brain.services.request_states import StateFollowing

from .platform import FakePlatform

READ_BACK = {
    "id": "6c1f6c1e-0000-4000-8000-000000000001",
    "number": 3,
    "state": "draft",
    "kind": "view",
    "title": "Orders by channel",
    "summary": "A board of confirmed orders by channel.",
    "model_name": "Sales Order",
    "rows": 1200,
}
CLIENT = "odoo.addons.dooservice_brain.models.brain_request.AssistantClient"


@tagged("post_install", "-at_install")
class TestRequests(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ana = new_test_user(cls.env, "ana", groups="base.group_user,dooservice_brain.group_request")

    def made(self):
        return self.env["dooservice.brain.request"].with_user(self.ana).create({"text": "Orders by channel"})

    def test_it_is_read_back_then_sent(self):
        request = self.made()
        platform = FakePlatform({"understand": READ_BACK, "submit": {**READ_BACK, "state": "queued"}})

        with patch(CLIENT, return_value=platform):
            request.action_understand()
            read_state = request.state
            request.action_submit()

        self.assertEqual(read_state, "draft")
        self.assertEqual((request.name, request.rows, request.state), ("Orders by channel", 1200, "queued"))
        self.assertEqual(platform.asked[0][1][3], "ana")

    def test_a_change_on_the_platform_is_told_in_the_chatter(self):
        request = self.made()
        request.sudo().write(StateFollowing.values_of({**READ_BACK, "state": "queued"}))
        platform = FakePlatform({"requests": {"requests": [{**READ_BACK, "state": "ready"}]}})

        StateFollowing(self.env, platform).follow()

        self.assertEqual(request.state, "ready")
        self.assertIn("In review", request.message_ids[0].body)

    def test_someone_sees_only_their_own_requests(self):
        self.made()
        luis = new_test_user(self.env, "luis", groups="base.group_user,dooservice_brain.group_request")

        self.assertFalse(self.env["dooservice.brain.request"].with_user(luis).search([]))
