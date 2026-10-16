"""The screen a ticket was opened from, said for the people in its chat; never sent to the platform."""

from odoo.exceptions import AccessError, MissingError


class ScreenLabel:
    def __init__(self, env):
        self.env = env

    def of(self, model, record_id):
        if not model or model not in self.env:
            return ""
        description = self.env["ir.model"].sudo()._get(model).name or model
        if not record_id:
            return description
        try:
            record = self.env[model].browse(int(record_id)).exists()
            name = record.display_name if record else ""
        except (AccessError, MissingError, ValueError):
            name = ""
        return f"{description} {name}".strip()
