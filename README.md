# Dooservice modules for Odoo, 16.0 to 20.0

Two modules: `dooservice_brain`, **Dooservice**, the tickets to your consultancy, and
`dooservice_connect`, signing in from the Dooservice panel.

## Dooservice

`dooservice_brain` (its technical name, kept for the databases that already have it) puts
the consultancy where the people who use Odoo already are: **tickets** with a chat each in
Discuss.

- **The bulb** in the top bar opens a ticket from any screen: a **question** (how something
  is done), an **incident** (something did not go as expected) or a **change** (make the
  system do something different). The screen and the record open go with it as a reference
  the AI never sees; nothing of the record itself leaves this Odoo.
- **One chat per ticket**, named `T-0002 · title`, with its kind, process and state over
  it. Dooservice answers from the processes the company's consultants reviewed and says
  which steps it stands on; what it cannot answer goes to the consultancy, with the hours
  it answers in and the deadline visible. A **change** is read back («Is it correct?»),
  rehearsed on a copy, approved and applied; the person who may only ask leaves it with
  the company's **Dooservice responsible**.
- **Pieces with buttons** under the bot's messages: «Was it resolved? Yes, close / No,
  continue», «Is it correct? Yes / Correct / Cancel», approve or decline, a rating. Nothing
  moves a ticket without pressing a button that says so, and a button does its thing once.
  A closed ticket takes no more messages: the bot offers a new ticket linked to it.
- **Dooservice › My tickets** lists one's own tickets with kind, process, state and when
  they last moved; the responsible also sees the team's.

What people write travels to the platform by a task every two minutes, and sooner when
someone writes; the platform's answers come back the same way, each posted once.

## Dooservice Connect

`dooservice_connect` signs a person in from **Open instance** in the panel as this Odoo's
administrator, as Connect does on Odoo.sh: the panel's account is never the person's Odoo
user. The panel decides who may (a developer of the environment; on production, only a
project admin) and signs a link for the address it opens, valid once and for a minute; this
Odoo checks it with the platform's public key, logs who came in, and sends anything it
cannot accept to its own login page.

It is a server-wide module, loaded from `odoo.conf` and never installed: a database taken
elsewhere carries nothing of it, and the links already used are remembered beside the
filestore, not in the database. The platform writes:

```ini
[options]
server_wide_modules = base,web,dooservice_connect
dooservice_connect_key = <the platform's public key, base64>
```

## Branches

One branch per Odoo version: `16.0`, `17.0`, `18.0`, `19.0`, `20.0`. The module is the
same in all of them; what differs is what each version of Odoo names differently.

## Setup

The module is part of the images of the Dooservice platform; it is not installed by
itself. The platform writes the project's key in `odoo.conf`, never in the database:

```ini
[options]
dooservice_assistant_key = dsa_...
dooservice_assistant_url = https://api.dooservice.sh/api/v2
```

Then install **Dooservice** from Apps. The administrator is the Dooservice responsible on
install; give everybody else one of its levels in their user form, under **Dooservice**:

| Level | What it allows |
|---|---|
| Ask and report | open questions and incidents from the bulb, and follow them in Discuss |
| Request changes | also ask for changes in how Odoo works |
| Dooservice responsible | also approve the changes asked by people who may only ask, and see the team's tickets |

## Tests

```sh
odoo -d test -i dooservice_brain --test-tags /dooservice_brain --stop-after-init
```

## License

LGPL-3.0, like Odoo's own modules.
