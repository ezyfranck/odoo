# Copyright 2018 - 2020 Mind And Go
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Add Specifics Order states for PS",
    "summary": """
        Logistics improvements
        """,
    "version": "14.0.2.0.1",
    "license": "AGPL-3",
    "description": """
    """,
    "author": "Mind And Go",
    "website": "https://www.mind-and-go.com",
    "category": "Custom Modules",
    # any module necessary for this one to work correctly
    "depends": [
        "logistics_improvements",
        # TODO : find the way to prevent the dependency of the following module
        "connector_prestashop",
        "sale_delivery_state",
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
