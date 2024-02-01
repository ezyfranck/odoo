# Copyright 2018 - 2020 Mind And Go
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Force Final partner by carrier",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Mind And Go",
    "website": "https://www.mind-and-go.com",
    "category": "Custom Modules",
    # any module necessary for this one to work correctly
    "depends": [
        "delivery",
        "delivery_dropoff_site",
        "sale_stock",
        "sale_order_type",
    ],
    # always loaded
    "data": [
        "views/delivery.xml",
        # "views/stock_picking.xml",
        # "views/sale_order.xml",
        # "views/partner.xml",
        # "views/product.xml",
        # "views/base_config.xml",
        # "security/ir.model.access.csv",
    ],
    # only loaded in demonstration mode
    "demo": [],
    "css": [],
    "test": [],
    "installable": True,
    "auto_install": False,
}
