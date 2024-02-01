# Copyright 2018 - 2020 Mind And Go
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Add dimensions from PS",
    "summary": """
        PS Logistics improvements
        """,
    "version": "1.0.1",
    "license": "AGPL-3",
    "author": "Mind And Go",
    "website": "https://www.mind-and-go.com",
    "category": "Custom Modules",
    # any module necessary for this one to work correctly
    "depends": [
        "product_dimension",
        "product_logistic_dimension",
        # TODO : find the way to prevent the dependency of this module
        "connector_prestashop",
    ],
    # always loaded
    "data": [
        #         'datas/efilog_config_data.xml',
        #         'views/delivery.xml',
        # #
        #         'views/stock_picking.xml',
        #         'views/sale_order.xml',
        #         'views/partner.xml',
        #         'views/product.xml',
    ],
    # only loaded in demonstration mode
    "demo": [],
    "css": [],
    "test": [],
    "installable": False,
    "auto_install": False,
}
