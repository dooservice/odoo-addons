"""How a link from the panel is checked, and where the links already used are remembered."""

#: The option of odoo.conf with the platform's public key, written there by the agent.
CONFIG_KEY = "dooservice_connect_key"
#: How late a link may arrive past its expiry, for a server's clock a little behind.
LEEWAY_SECONDS = 30
#: Under the data dir, outside the database: a backup taken elsewhere carries none of it.
USED_FOLDER = "dooservice_connect"
#: A used link is remembered for longer than it could ever be valid.
USED_KEPT_SECONDS = 10 * 60
#: Where a signed-in person lands.
LANDING = "/web"
#: What a person reads when a link does not sign them in; the reason stays in the log.
REFUSED = "This link from the Dooservice panel does not work any more. Ask for a new one."
NOT_READY = "Dooservice Connect is not set up on this Odoo yet: it will be after its next restart."
