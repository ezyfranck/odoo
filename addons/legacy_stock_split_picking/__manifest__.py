# Copyright 2013-2015 Camptocamp SA - Nicolas Bessi
# Copyright 2013-2015 Camptocamp SA - Guewen Baconnier
# Copyright 2013-2015 Camptocamp SA - Yannick Vaucher
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Re-Introduce v10 behaviour for Split picking",
    "summary": "Split a picking in two not transferred pickings",
    "version": "14.0.1.1.0",
    "category": "Inventory",
    "author": "Mind And Go, "
    "Camptocamp, "
    "Tecnativa, "
    "Odoo Community Association (OCA),",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock", "stock_split_picking"],
    "data": [
        # "security/ir.model.access.csv",
        "wizards/stock_split_picking.xml",
        # "views/stock_partial_picking.xml",
    ],
}
