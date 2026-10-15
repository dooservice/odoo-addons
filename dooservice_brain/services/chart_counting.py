"""The figures of a chart in the chat, counted by this Odoo with the person's own access.

Only what the person may read is counted, and only by the field the platform named; the
platform never sees the figures.
"""

from odoo import _
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
            records.check_access_rights("read")
            with self.env.cr.savepoint():
                groups = records.read_group([], [group_by], [grouped])
        except AccessError:
            return {"denied": "access"}
        except (UserError, ValueError):
            return {"denied": "unknown"}
        counted = [(group[grouped], group.get(f"{group_by}_count") or group.get("__count") or 0) for group in groups]
        counted.sort(key=lambda pair: pair[1], reverse=True)
        return {
            "groups": [
                {"label": self.label(field, value), "count": count} for value, count in counted[:CHART_GROUPS_MAX]
            ]
        }

    def label(self, field, value):
        if not value:
            return _("None")
        if field.type == "many2one":
            return value[1]
        if field.type == "selection":
            return dict(field._description_selection(self.env)).get(value, value)
        return str(value)
