"""Where the platform is, what a ticket can be, and what a person may do with the pieces of a message."""

#: The options of odoo.conf the platform writes for this database: never stored in it.
CONFIG_KEY = "dooservice_assistant_key"
CONFIG_URL = "dooservice_assistant_url"
#: Where the platform answers when odoo.conf names no other address.
DEFAULT_URL = "https://api.dooservice.sh/api/v2"
#: The routes of the platform this module talks to, under its address.
API_PREFIX = "/business/odoo"

#: The platform waits two minutes for a slow model; the call waits a little longer.
TIMEOUT_SECONDS = 150
#: How long the status of the platform, hours and reviewed processes, is kept before asking again.
STATUS_KEPT_SECONDS = 10 * 60
#: The longest text the platform takes in one message, in characters.
TEXT_MAX_CHARACTERS = 2000
#: How many open tickets one run of the sync task refreshes before it lets another run.
TICKETS_PER_RUN = 50

#: The XML ids this module is found by.
BOT_PARTNER = "dooservice_brain.partner_dooservice"
BOT_USER = "dooservice_brain.user_dooservice"
GROUP_ASK = "dooservice_brain.group_ask"
GROUP_REQUEST = "dooservice_brain.group_request"
GROUP_RESPONSIBLE = "dooservice_brain.group_responsible"
SYNC_CRON = "dooservice_brain.cron_sync_tickets"
DISCUSS_ACTION = "mail.action_discuss"
NEW_TICKET_ACTION = "dooservice_brain.new_ticket"

#: How a ticket is named in its chat and its list: the prefix and the width of its number.
TICKET_PREFIX = "T-"
TICKET_NUMBER_WIDTH = 4

#: The kinds of ticket, as the platform names them.
TICKET_KINDS = [("question", "Question"), ("incident", "Incident"), ("change", "Change"), ("report", "Report")]
#: The states of a ticket, as the platform names them.
TICKET_STATES = [
    ("open", "Open"),
    ("running", "In progress"),
    ("waiting_consultant", "Waiting for the consultancy"),
    ("waiting_user", "Waiting for your answer"),
    ("resolved", "Resolved"),
    ("closed", "Closed"),
]
#: Where a change ticket stands, as the platform names it.
CHANGE_STAGES = [
    ("opened", "Opened"),
    ("understood", "Understood"),
    ("plan", "Planned"),
    ("rehearsal", "Rehearsed"),
    ("to_approve", "To approve"),
    ("applied", "Applied"),
    ("verified", "Verified"),
    ("closed", "Closed"),
    ("rejected", "Rejected"),
    ("undone", "Undone"),
    ("out_of_scope", "Out of scope"),
]
#: Who a waiting ticket waits for.
WAITING_FOR = [("consultant", "The consultancy"), ("responsible", "The Dooservice responsible"), ("user", "You")]
#: Who wrote a message the platform returns.
MESSAGE_AUTHORS = ("user", "assistant", "consultant", "responsible", "system")
#: Tickets in these states change no more.
CLOSED_STATES = ("closed",)

#: What a person may do with a piece, by its type; pieces without actions are only read.
CARD_ACTIONS = {
    "resolved": ("yes", "no"),
    "understood": ("yes", "correct", "cancel"),
    "approval": ("approve", "decline"),
    "rating": ("rate",),
}
#: The piece the bot adds itself when a closed ticket is written to.
CONTINUE_CARD = "continue"
#: The ratings a person gives an answer.
RATINGS = ("up", "down")
#: The pieces only a Dooservice responsible may press.
RESPONSIBLE_CARDS = ("approval",)
