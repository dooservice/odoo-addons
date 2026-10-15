from odoo import models


class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    def _message_post_after_hook(self, message):
        self.env["dooservice.brain.question"]._receive(self, message)
        return super()._message_post_after_hook(message)
