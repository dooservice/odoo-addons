"""The old brain leaves: its questions and requests, their tables, and the single chat with the bot.

Tickets replace them; nothing of the old data is kept, as the contract says.
"""

from odoo import SUPERUSER_ID, api

MODULE = "dooservice_brain"
OLD_TABLES = ("dooservice_brain_question", "dooservice_brain_request")
OLD_MODELS = ("dooservice.brain.question", "dooservice.brain.request")
OLD_XMLID_PATTERNS = (
    "model_dooservice_brain_%",
    "field_dooservice_brain_%",
    "selection__dooservice_brain_%",
    "constraint_dooservice_brain_%",
    "access_question_%",
    "access_request_%",
    "rule_question_%",
    "rule_request_%",
    "view_request_%",
    "action_requests",
    "menu_requests",
    "cron_answer_questions%",
    "cron_follow_requests%",
)
BOT_PARTNER = "partner_dooservice"


class OldBrain:
    def __init__(self, cr):
        self.cr = cr
        self.env = api.Environment(cr, SUPERUSER_ID, {})

    def remove(self):
        self.drop_chats()
        self.drop_records()
        self.drop_tables()

    def old_ids(self, model):
        self.cr.execute(
            "SELECT res_id FROM ir_model_data WHERE module = %s AND model = %s AND name LIKE ANY(%s)",
            (MODULE, model, list(OLD_XMLID_PATTERNS)),
        )
        return tuple(row[0] for row in self.cr.fetchall()) or (0,)

    def drop_chats(self):
        """The one-to-one chats with the bot, with their messages; ticket channels are groups and stay."""
        self.cr.execute("SELECT res_id FROM ir_model_data WHERE module = %s AND name = %s", (MODULE, BOT_PARTNER))
        row = self.cr.fetchone()
        if not row:
            return
        self.cr.execute(
            "SELECT DISTINCT c.id FROM mail_channel c JOIN mail_channel_member m ON m.channel_id = c.id "
            "WHERE c.channel_type = 'chat' AND m.partner_id = %s",
            (row[0],),
        )
        channels = self.env["mail.channel"].browse([line[0] for line in self.cr.fetchall()])
        if channels:
            channels.unlink()

    def drop_records(self):
        """Crons, menus, actions and views of the old models go first; the models take fields, access and rules."""
        self.cr.execute("DELETE FROM ir_cron WHERE id IN %s", (self.old_ids("ir.cron"),))
        servers = self.old_ids("ir.actions.server")
        self.cr.execute("DELETE FROM ir_act_server WHERE id IN %s", (servers,))
        self.cr.execute("DELETE FROM ir_actions WHERE id IN %s", (servers,))
        self.cr.execute("DELETE FROM ir_ui_menu WHERE id IN %s", (self.old_ids("ir.ui.menu"),))
        actions = self.old_ids("ir.actions.act_window")
        self.cr.execute("DELETE FROM ir_act_window WHERE id IN %s", (actions,))
        self.cr.execute("DELETE FROM ir_actions WHERE id IN %s", (actions,))
        self.cr.execute("DELETE FROM ir_ui_view WHERE model IN %s", (OLD_MODELS,))
        self.cr.execute("DELETE FROM ir_model WHERE model IN %s", (OLD_MODELS,))
        self.cr.execute(
            "DELETE FROM ir_model_data WHERE module = %s AND name LIKE ANY(%s)", (MODULE, list(OLD_XMLID_PATTERNS))
        )

    def drop_tables(self):
        for table in OLD_TABLES:
            self.cr.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')


def migrate(cr, version):
    OldBrain(cr).remove()
