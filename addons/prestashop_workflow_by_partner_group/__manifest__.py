# Copyright 2018 - 2020 Mind And Go
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Match Partner group to get proper workflow",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Mind And Go",
    "website": "https://www.mind-and-go.com",
    "category": "Custom Modules",
    # any module necessary for this one to work correctly
    "depends": [
        "account",
        "connector_prestashop",
        "sale_automatic_workflow_payment_mode",
        "sale_automatic_workflow",
    ],
    # always loaded
    "data": [
        "views/sale_workflow_process_view.xml",
        "views/fiscal_position.xml",
        "views/prestashop_category.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
    "css": [],
    "test": [],
    "installable": True,
    "auto_install": False,
}
