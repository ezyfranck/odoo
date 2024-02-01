# Copyright 2018 - 2020 Mind And Go
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Cancel inventory api",
    "summary": """
        Cancel inventory api
        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "description": """
        * EFILOG
        * L4
        * GTL
        * ELOGIK
        * Welcome Track
    """,
    "author": "Mind And Go",
    "website": "https://www.mind-and-go.com",
    "category": "Custom Modules",
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "sale_stock",
    ],
    # always loaded
    "data": [],
    # only loaded in demonstration mode
    "demo": [],
    "css": [],
    "test": [],
    "installable": False,
    "auto_install": False,
}
