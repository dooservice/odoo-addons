{
    "name": "Dooservice Assistant",
    "summary": "Ask how your company works in Odoo, and request new views",
    "description": "Chat with Dooservice in Discuss: it answers from the processes your consultants reviewed, "
    "and turns what you want to see into a request they build and approve.",
    "version": "18.0.1.1.0",
    "category": "Productivity/Discuss",
    "license": "LGPL-3",
    "author": "Dooservice",
    "website": "https://dooservice.sh",
    "depends": ["mail"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/rules.xml",
        "data/partner.xml",
        "data/crons.xml",
        "views/request_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "dooservice_brain/static/src/**/*",
        ],
    },
    "installable": True,
    "application": False,
}
