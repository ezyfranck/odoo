# -*- coding: utf-8 -*-
#  © 2019 ToDay Mind&GO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models
from odoo.addons.sale.models import product_product
from odoo.addons.product.models import product_template


class Bom(models.Model):
    _inherit = 'mrp.bom'

    assembly = fields.Char()
