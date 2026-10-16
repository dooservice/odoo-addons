from odoo import models

from ..services.message_intake import MessageIntake


class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    def _message_post_after_hook(self, message):
        MessageIntake(self.env).receive(self, message)
        return super()._message_post_after_hook(message)
