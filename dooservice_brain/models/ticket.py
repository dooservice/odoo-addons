"""A ticket to Dooservice, followed here from the platform, with a chat of its own in Discuss.

The platform owns the ticket; this record keeps what the person sees of it: its number,
kind, state and process, and the chat where the conversation happens.
"""

from odoo import api, fields, models

from ..constants import (
    CHANGE_STAGES,
    DISCUSS_ACTION,
    NEW_TICKET_ACTION,
    TICKET_KINDS,
    TICKET_NUMBER_WIDTH,
    TICKET_PREFIX,
    TICKET_STATES,
    WAITING_FOR,
)
from ..services.bot_posting import BotPosting
from ..services.screen_label import ScreenLabel
from ..services.ticket_header import TicketHeader
from ..services.ticket_opening import TicketOpening
from ..services.ticket_sync import TicketSync


class Ticket(models.Model):
    _name = "dooservice.ticket"
    _description = "Dooservice ticket"
    _order = "write_date desc, id desc"
    _rec_name = "number"

    remote_number = fields.Integer(string="Number on the platform", required=True, index=True, readonly=True)
    number = fields.Char(compute="_compute_number", store=True, readonly=True)
    kind = fields.Selection(TICKET_KINDS, required=True, readonly=True)
    title = fields.Char(readonly=True)
    text = fields.Text(string="What was asked", readonly=True)
    state = fields.Selection(TICKET_STATES, default="open", required=True, readonly=True, index=True)
    change_stage = fields.Selection(CHANGE_STAGES, readonly=True)
    waiting_for = fields.Selection(WAITING_FOR, readonly=True)
    channel_id = fields.Many2one("discuss.channel", string="Chat", readonly=True, ondelete="set null", index=True)
    user_id = fields.Many2one(
        "res.users", string="Opened by", required=True, readonly=True, ondelete="cascade", index=True
    )
    process_name = fields.Char(string="Process", readonly=True)
    deadline = fields.Datetime(readonly=True)
    screen_model = fields.Char(readonly=True)
    record_id = fields.Integer(readonly=True)
    continues_id = fields.Many2one("dooservice.ticket", string="Continues", readonly=True, ondelete="set null")
    last_sync = fields.Datetime(readonly=True)

    @api.depends("remote_number")
    def _compute_number(self):
        for ticket in self:
            ticket.number = f"{TICKET_PREFIX}{ticket.remote_number:0{TICKET_NUMBER_WIDTH}d}"

    def channel_name(self):
        self.ensure_one()
        return f"{self.number} · {self.title}" if self.title else self.number

    def notice(self, text):
        self.ensure_one()
        return BotPosting(self.env).notice(self.channel_id, text)

    def action_open_chat(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(DISCUSS_ACTION)
        action["params"] = {"active_id": f"discuss.channel_{self.channel_id.id}"}
        return action

    def action_new_ticket(self):
        return {"type": "ir.actions.client", "tag": NEW_TICKET_ACTION}

    @api.model
    def open_ticket(self, kind, text, screen_model="", record_id=0, continues=None):
        """From the bulb: the ticket is opened on the platform and its chat made; the browser opens the chat."""
        ticket = TicketOpening(self.env).open(kind, text, screen_model, record_id, continues)
        return {"id": ticket.id, "channel_id": ticket.channel_id.id, "number": ticket.number}

    @api.model
    def header_of(self, channel_id):
        """What the chat shows over a ticket: its kind, state and process; nothing for other chats."""
        return TicketHeader(self.env).of(channel_id)

    @api.model
    def screen_label(self, screen_model, record_id):
        """The screen the bulb was pressed on, said for the dialog; nothing leaves this Odoo."""
        return ScreenLabel(self.env).of(screen_model, record_id)

    @api.model
    def _sync_open(self):
        TicketSync(self.env, checkpoint=self.env.cr.commit).run()
