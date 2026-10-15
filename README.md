# Dooservice Assistant for Odoo, 16.0 to 20.0

`dooservice_brain` puts the project's brain where the people who use Odoo already are:
a chat with **Dooservice** in Discuss.

- **Ask** how the company works in Odoo: who approves a discount, when an invoice is
  sent. The answer comes only from the processes the company's consultants reviewed,
  and says which steps it stands on. The AI sees no record of this Odoo.
- **Request** a list, a board or a report in your own words. You see what was understood,
  on about how many records, before you send it. Your consultant builds it as a module
  in the project's repository, reviews it and approves it; it arrives with the next
  deploy. Each change of state is written in the request's chatter.

Every answer says which model wrote it and on whose AI account. Questions and answers
stay in this database.

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

Then install **Dooservice Assistant** from Apps, and give people one of its groups:

| Group | What it allows |
|---|---|
| Dooservice Assistant: ask | chat with Dooservice |
| Dooservice Assistant: request changes | also send requests and follow them under **Dooservice › Requests** |

## Tests

```sh
odoo -d test -i dooservice_brain --test-tags /dooservice_brain --stop-after-init
```

## License

LGPL-3.0, like Odoo's own modules.
