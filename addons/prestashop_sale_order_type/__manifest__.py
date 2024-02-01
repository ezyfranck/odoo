# Copyright 2018 - 2020 Mind And Go
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Force Final partner by carrier",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Mind And Go",
    "website": "https://www.mind-and-go.com",
    "category": "Custom Modules",
    # any module necessary for this one to work correctly
    "depends": [
        "connector_prestashop",
        "sale_order_type",
        "final_partner_delivery_carrier",
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
