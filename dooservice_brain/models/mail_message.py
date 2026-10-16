"""What a message in a ticket chat carries besides its text: its pieces, what people chose, and where it stands.

Kept on the message itself, in this database. A message of the platform remembers the
platform's id so it is posted once; a person's message waits as pending until the sync
task carries it to the platform.
"""

from odoo import fields, models


class MailMessage(models.Model):
    _inherit = "mail.message"

    dooservice_cards = fields.Json(copy=False)
    dooservice_card_state = fields.Json(copy=False)
    dooservice_remote_id = fields.Integer(copy=False, index=True)
    dooservice_pending = fields.Boolean(copy=False, index=True)
