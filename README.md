# Dooservice Connect for Odoo, 16.0 to 20.0

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

## Tests

```sh
odoo -d test -i dooservice_connect --test-tags /dooservice_connect --stop-after-init
```

## License

LGPL-3.0, like Odoo's own modules.
