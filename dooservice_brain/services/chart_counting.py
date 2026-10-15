"""The figures of a chart in the chat, counted by this Odoo with the person's own access.

Only what the person may read is counted, and only by the field the platform named; the
platform never sees the figures.
"""

from odoo.exceptions import AccessError, UserError

from ..constants import CHART_GROUPS_MAX

DATED = ("date", "datetime")


class ChartCounting:
    def __init__(self, env):
        self.env = env

    def count(self, card):
        model, group_by = card.get("model") or "", card.get("group_by") or ""
        if model not in self.env or group_by not in self.env[model]._fields:
            return {"denied": "unknown"}
        records = self.env[model]
        field = records._fields[group_by]
        grouped = f"{group_by}:month" if field.type in DATED else group_by
        try:
            records.check_access("read")
            with self.env.cr.savepoint():
                groups = records._read_group([], [grouped], ["__count"], order="__count desc", limit=CHART_GROUPS_MAX)
        except AccessError:
            return {"denied": "access"}
        except (UserError, ValueError):
            return {"denied": "unknown"}
        return {"groups": [{"label": self.label(field, value), "count": count} for value, count in groups]}

    def label(self, field, value):
        if not value:
            return self.env._("None")
        if field.type == "many2one":
            return value.sudo().display_name
        if field.type == "selection":
            return dict(field._description_selection(self.env)).get(value, value)
        if field.type in DATED:
            return value.strftime("%Y-%m")
        return str(value)
