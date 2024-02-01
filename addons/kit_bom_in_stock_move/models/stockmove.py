# -*- coding: utf-8 -*-
#  © 2019 ToDay Mind&GO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models
from odoo.addons.sale.models import product_product
from odoo.addons.product.models import product_template


class StockMove(models.Model):
    _inherit = 'stock.move'

    kit_bom_id = fields.Many2one('mrp.bom', string='Nomenclature kit', copy=True)

    @api.model
    def create(self, vals):
        mv = super(StockMove, self).create(vals)
        kit_bom_id = False
        if vals.get('move_dest_id'):
            dest_id = self.browse(vals.get('move_dest_id'))
            if dest_id.kit_bom_id:
                kit_bom_id = dest_id.kit_bom_id
        if vals.get('bom_line_id') and kit_bom_id ==False:
            kit_bom_id=self.env['mrp.bom.line'].browse(vals.get('bom_line_id')).bom_id
        if mv.move_dest_ids and kit_bom_id == False:
            kit_bom_id = mv.move_dest_ids[0].kit_bom_id
        if not kit_bom_id:
            kit_bom_id = self.env['mrp.bom']._bom_find(
                product_tmpl=mv.product_id.product_tmpl_id,
                product=mv.product_id,
            )
        mv.kit_bom_id = kit_bom_id
        return mv

    def _generate_move_phantom(self, bom_line, quantity,quantity_done):
        res = super(StockMove, self)._generate_move_phantom(bom_line, quantity,quantity_done)

        if bom_line.product_id.type in ['product', 'consu']:
            res[0].update({'kit_bom_id': bom_line.bom_id.id})

        return res
