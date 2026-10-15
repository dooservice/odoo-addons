from odoo import api, fields, models

from ..constants import BOT_PARTNER, GROUP_ASK


class ResUsers(models.Model):
    _inherit = "res.users"

    dooservice_brain_screen = fields.Char(
        string="Screen asked from",
        help="The model of the screen this person last opened the assistant from.",
    )

    @api.model
    def dooservice_brain_open(self, screen_model=""):
        """The assistant's partner, for the browser to open its chat; the screen is remembered for the next question."""
        if not self.env.user.has_group(GROUP_ASK):
            return False
        self.env.user.sudo().dooservice_brain_screen = screen_model or False
        self._dooservice_brain_chat()
        return self.env.ref(BOT_PARTNER).id

    @api.model
    def _dooservice_brain_chat(self):
        """This person's chat with Dooservice, made the first time."""
        return self.env["discuss.channel"]._get_or_create_chat([self.env.ref(BOT_PARTNER).id])
