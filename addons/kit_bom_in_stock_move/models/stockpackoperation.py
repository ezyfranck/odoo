# -*- coding: utf-8 -*-
#  © 2019 ToDay Mind&GO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models
from odoo.addons.sale.models import product_product
from odoo.addons.product.models import product_template


class StockPackOperation(models.Model):
    _inherit = 'stock.picking'

    kit_bom_id = fields.Many2one('mrp.bom', string='Nomenclature kit', compute='_update_bom')

    @api.depends('move_ids_without_package')
    def _update_bom(self):
        for op in self:
            if op.move_ids_without_package:
                op.kit_bom_id = op.move_ids_without_package[0].move_id.kit_bom_id
