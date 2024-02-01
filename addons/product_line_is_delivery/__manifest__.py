# Copyright 2018 - 2020 Mind And Go
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Change is_delivery in order sale line",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "description": """
    sale order line, with service product, this line isn't delivery
    """,
    "author": "Gael Torrecillas - Mind And Go",
    "website": "https://www.mind-and-go.com",
    "category": "Custom Modules",
    # any module necessary for this one to work correctly
    "depends": [
        "sale",
        "delivery",
    ],
    # always loaded
    "data": [],
    # only loaded in demonstration mode
    "demo": [],
    "css": [],
    "test": [],
    "installable": True,
    "auto_install": False,
}
