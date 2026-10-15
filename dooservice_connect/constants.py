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
#: Where a link that cannot sign anybody in sends them: Odoo's own login, never a dead end.
#: Why it did not is only in the log.
SIGN_IN = "/web/login"
