"""The line under the bulb: when the consultancy answers, said from what the platform knows of the project."""

from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate("dooservice_brain")


class StatusLine:
    weekdays = (_lt("Mon"), _lt("Tue"), _lt("Wed"), _lt("Thu"), _lt("Fri"), _lt("Sat"), _lt("Sun"))

    def __init__(self, env):
        self.env = env

    def of(self, status):
        hours = status.get("support_hours") or {}
        days = self.days(hours.get("weekdays") or [])
        if not days or not hours.get("start") or not hours.get("end"):
            return self.env._(
                "Your consultancy answers within %(hours)s working hours.", hours=status.get("response_hours") or 4
            )
        return self.env._(
            "Your consultancy answers %(days)s %(start)s–%(end)s within %(hours)s working hours.",
            days=days,
            start=hours["start"],
            end=hours["end"],
            hours=status.get("response_hours") or 4,
        )

    def days(self, weekdays):
        """Weekdays 1–7 as the platform counts them; a run of days is said by its ends."""
        lang = self.env.lang or ""
        names = [self.weekdays[day - 1]._translate(lang) for day in sorted(set(weekdays)) if 1 <= day <= 7]
        if not names:
            return ""
        chosen = sorted(set(day for day in weekdays if 1 <= day <= 7))
        if len(chosen) > 2 and chosen == list(range(chosen[0], chosen[-1] + 1)):
            return f"{names[0]}–{names[-1]}"
        return ", ".join(names)
