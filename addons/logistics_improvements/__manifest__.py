# Copyright 2018 - 2020 Mind And Go
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Logistics customizations",
    "summary": """
        Logistics improvements
        """,
    "version": "16.0.4.0.2",
    "license": "AGPL-3",
    "author": "Mind And Go",
    "website": "https://www.mind-and-go.com",
    "category": "Custom Modules",
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "product",
        "delivery",
        "delivery_carrier_default_tracking_url",
        "stock",
        "sale_stock",
        "sale_automatic_workflow",
        "product_dimension",
        "stock_picking_sale_order_link",
        "uom",
        "base_substate",
        "product_packaging_level",
        "packaging_uom"
        # TODO : find the way to prevent the dependency of this module
        # 'connector_prestashop'
    ],
    # always loaded
    "data": [
        "views/delivery.xml",
        "views/stock_picking.xml",
        "views/sale_order.xml",
        "views/partner.xml",
        "views/product.xml",
        "views/base_config.xml",
        "security/ir.model.access.csv",
        "security/logistics_security.xml",
        "datas/logistics_substates.xml",
        "datas/packaging_type.xml",
        "views/packaging_views.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
    "css": [],
    "test": [],
    "installable": True,
    "auto_install": False,
}
