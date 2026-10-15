"""The pieces an answer of the assistant carries under its text, and what people chose in them.

Kept on the message itself, in this database: a choice made, a draft sent or cancelled, a
rating given. Nothing of it is a record of the business.
"""

from odoo import fields, models


class MailMessage(models.Model):
    _inherit = "mail.message"

    dooservice_cards = fields.Json(copy=False)
    dooservice_card_state = fields.Json(copy=False)
