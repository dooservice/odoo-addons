"""A request for something new in this Odoo, followed here while the platform builds and reviews it.

It starts as the person's words. Reading it back asks the platform what it understood;
sending it is the person's confirmation. Its state is followed from the platform, and
each change is written in its chatter for whoever asked.
"""

from odoo import api, fields, models
from odoo.exceptions import UserError

from ..services.client import AssistantClient, AssistantError
from ..services.request_states import KINDS, STATES, StateFollowing
from ..services.wording import Wording


class BrainRequest(models.Model):
    _name = "dooservice.brain.request"
    _description = "Request to the Dooservice assistant"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(string="Title", tracking=True)
    text = fields.Text(string="What you want", required=True)
    summary = fields.Text(string="What was understood", readonly=True)
    kind = fields.Selection(KINDS, readonly=True)
    state = fields.Selection(STATES, default="new", required=True, readonly=True, tracking=True)
    number = fields.Integer(readonly=True)
    remote_id = fields.Char(readonly=True, copy=False, index=True)
    model_name = fields.Char(string="About", readonly=True)
    rows = fields.Integer(string="Records, about", readonly=True)
    screen_model = fields.Char(readonly=True)
    review_comment = fields.Text(string="Consultant's comment", readonly=True)
    requested_by = fields.Many2one("res.users", default=lambda self: self.env.user, required=True, readonly=True)
    message_id = fields.Many2one("mail.message", readonly=True, ondelete="set null", help="The chat piece it was sent from.")

    def refused(self, error):
        raise UserError(Wording.refusal(error.code, self.env.user.lang or ""))

    def action_understand(self):
        self.ensure_one()
        user = self.requested_by
        try:
            read = AssistantClient().understand(
                self.text, self.screen_model or "", (user.lang or "en")[:2], user.login, user.name
            )
        except AssistantError as error:
            self.refused(error)
        self.write(StateFollowing.values_of(read))
        return True

    def action_submit(self):
        self.ensure_one()
        try:
            sent = AssistantClient().submit(self.remote_id)
        except AssistantError as error:
            self.refused(error)
        self.write(StateFollowing.values_of(sent))
        return True

    def action_cancel(self):
        for request in self:
            if request.remote_id:
                try:
                    request.write(StateFollowing.values_of(AssistantClient().cancel(request.remote_id)))
                except AssistantError as error:
                    request.refused(error)
            else:
                request.state = "cancelled"
        return True

    @api.model
    def _from_question(self, question):
        """A refusal leaves it new: the form says why when the person reads it back again."""
        request = self.create({"text": question.text, "screen_model": question.screen_model})
        try:
            request.action_understand()
        except UserError:
            return request
        return request

    @api.model
    def _follow_open(self):
        StateFollowing(self.env).follow()
