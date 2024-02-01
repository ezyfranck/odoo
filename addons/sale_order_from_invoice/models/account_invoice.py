# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError
import logging
import re

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.move'


    def get_order_ids(self):
        action_rec = self.env.ref('sale.action_quotations')
        action_copy = action_rec.read([])[0].copy()
        action_copy['domain'] = [('id', 'in', [s.id for s in self.sale_order_ids])]
        return action_copy


    @api.depends('invoice_line_ids')
    def _get_order_ids(self):
        for inv in self:
            sale_order_ids = self.env['sale.order']
            for l in inv.invoice_line_ids:
                sale_order_ids |= l.sale_line_ids.mapped('order_id')
            inv.sale_order_ids = sale_order_ids
            inv.sale_order_count = len(sale_order_ids)

    
    sale_order_ids = fields.Many2many(
        compute=_get_order_ids,
        comodel_name='sale.order',
        string="Associated Orders")

    sale_order_count = fields.Integer(
        compute=_get_order_ids,
        string="# Associated Orders",
        store=False)
    

        
    
    
        
        