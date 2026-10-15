"""Where the assistant answers from, how long it waits, and what it keeps of a conversation."""

#: The options of odoo.conf the platform writes for this database: never stored in it.
CONFIG_KEY = "dooservice_assistant_key"
CONFIG_URL = "dooservice_assistant_url"
#: Where the platform answers when odoo.conf names no other address.
DEFAULT_URL = "https://api.dooservice.sh/api/v2"

#: The platform waits two minutes for a slow model; the call waits a little longer.
TIMEOUT_SECONDS = 150
#: How many earlier messages of the chat travel with a question.
HISTORY_TURNS = 6
#: How many questions one run of the answering task takes before it lets another run.
QUESTIONS_PER_RUN = 20
#: How long the line under each answer, which model and whose account, is kept before asking again.
STATUS_KEPT_SECONDS = 10 * 60

#: The longest question the platform takes, in characters.
QUESTION_MAX_CHARACTERS = 2000

#: The XML ids this module is found by.
BOT_PARTNER = "dooservice_brain.partner_dooservice"
GROUP_ASK = "dooservice_brain.group_ask"
GROUP_REQUEST = "dooservice_brain.group_request"
ANSWER_CRON = "dooservice_brain.cron_answer_questions"

#: The pieces the module adds to an answer besides the ones the platform sends.
SOURCES_CARD = "sources"
META_CARD = "meta"
FEEDBACK_CARD = "feedback"
ERROR_CARD = "error"
DRAFT_CARD = "draft"
CHOICE_CARDS = ("choice", "multi", "field")
#: What a person may do with a piece, by its type.
CARD_ACTIONS = {
    "choice": ("choose",),
    "multi": ("choose",),
    "field": ("choose",),
    "draft": ("send", "cancel", "correct", "cancel_request"),
    "feedback": ("rate",),
    "error": ("retry",),
}
#: The ratings a person gives an answer.
RATINGS = ("up", "down")
#: The group of the administrators, who see every request and send the ones asked of them.
GROUP_SYSTEM = "base.group_system"
#: How many groups a chart in the chat draws, the largest first.
CHART_GROUPS_MAX = 12
#: Requests in these states change no more: their piece stops asking for news.
FINISHED_REQUEST_STATES = ("deployed", "rejected", "cancelled", "failed")
#: The refusals worth trying again a minute later: the platform or the model was away.
RETRIABLE = ("assistant_unreachable", "assistant_not_ready")
