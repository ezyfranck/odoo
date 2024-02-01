##############################################################################
#
#    L4 Specifications
#    Copyright (C) 2016 EZYTAIL (http://ezytail.com/)
#    @author: Bruno Rizo <bruno.rizo@mind-and-go.com>
#    @author Florent THOMAS <florent.thomas@mind-and-go.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "International Invoice Improvements",
    "summary": """
        Improvements for making invoice compatible""",
    "description": """

    """,
    "author": "Mind And Go",
    "website": "http://www.mind-and-go.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    "category": "Custom Modules",
    "version": "16.0.1.0",
    # any module necessary for this one to work correctly
    "depends": [
        "sale",
        "account",
        "product",
        "delivery",
        "sale_stock",
        "sale_order_from_invoice",
        #                 'sale_proforma_quotation',
        "stock_picking_invoice_link",
        #                'sale_order_from_invoice',
        "product_harmonized_system",
    ],
    # always loaded
    "data": [
        "views/account_invoice.xml",
        "views/sale_order.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        #         'demo.xml',
    ],
    "css": [],
    "test": [],
    "installable": True,
    "auto_install": False,
}
