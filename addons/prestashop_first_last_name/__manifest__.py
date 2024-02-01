# Copyright 2018 - 2020 Mind And Go
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "No Alias in adress mapping",
    "summary": """
        Prestashop Address improvements
        """,
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "description": """
    """,
    "author": "Mind And Go",
    "website": "https://www.mind-and-go.com",
    "category": "Custom Modules",
    # any module necessary for this one to work correctly
    "depends": [
        "connector_prestashop"
        # TODO : find the way to prevent the dependency of this module
        #'connector_prestashop'
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
    "installable": True,
    "auto_install": False,
}
