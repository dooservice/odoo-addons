{
    "name": "Dooservice",
    "summary": "Open tickets to your consultancy from any screen, and follow them in Discuss",
    "description": "Questions, incidents and changes go to Dooservice as tickets, each with its own chat in "
    "Discuss: it answers from the processes your consultants reviewed, and carries what needs them to them.",
    "version": "17.0.2.0.0",
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
        "views/ticket_views.xml",
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
