"""What the chat shows over a ticket: its number, kind, state and process, in the person's language."""

from ..constants import CLOSED_STATES


class TicketHeader:
    def __init__(self, env):
        self.env = env

    def of(self, channel_id):
        ticket = self.env["dooservice.ticket"].search([("channel_id", "=", int(channel_id))], limit=1)
        if not ticket:
            return False
        fields = ticket._fields
        kinds = dict(fields["kind"]._description_selection(self.env))
        states = dict(fields["state"]._description_selection(self.env))
        return {
            "id": ticket.id,
            "number": ticket.number,
            "kind": ticket.kind,
            "kind_label": kinds.get(ticket.kind, ticket.kind),
            "state": ticket.state,
            "state_label": states.get(ticket.state, ticket.state),
            "process": ticket.process_name or "",
            "closed": ticket.state in CLOSED_STATES,
        }
