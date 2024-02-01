# -*- coding: utf-8 -*-

import logging
import openerp.addons.decimal_precision as dp
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError
from functools import *

_logger = logging.getLogger(__name__)

class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'
      
    origin_country_id = fields.Many2one(
        'res.country', string='Country of Origin',
        related="product_id.origin_country_id",
        help="Country of origin of the product i.e. product "
        "'made in ____'.")

    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'product_id' in vals:
                product = self.env['product.product'].browse(vals['product_id'])
                hs_code = product.get_hs_code_recursively()
                if hs_code:
                    vals.update({'hs_code_id' : hs_code.id})
        lines = super(AccountInvoiceLine, self).create(vals_list)
        for line in lines:
            line._compute_untaxed_price()
        return lines
    
    @api.depends('price_unit', 'discount', 'tax_ids', 'quantity',
        'product_id', 'move_id.partner_id', 'move_id.currency_id')
    def _compute_untaxed_price(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.tax_ids.compute_all(price, quantity=1 , product=self.product_id, partner=self.move_id.partner_id)
        self.untaxed_price_unit = taxes['total_excluded']
        if self.move_id:
            self.untaxed_price_unit = self.move_id.currency_id.round(self.untaxed_price_unit)
    
    
    untaxed_price_unit = fields.Float(string='Unit Price', required=True,
                                digits= dp.get_precision('Product Price'),
                                default=_compute_untaxed_price)
    
    
        

class AccountInvoice(models.Model):
    _inherit = "account.move"

    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Delivery Carrier',
        compute='_compute_delivery_carrier')
    
    
    @api.depends('invoice_line_ids','carrier_id')
    def calc_sub_total(self):
        for inv in self:
            ht_carrier = 0.0
            lines = inv.invoice_line_ids.filtered(lambda r: r.product_id == inv.carrier_id.product_id)
            if len(lines) > 0 :
                ht_carrier=reduce(lambda x,y: x+y,
                        [z.price_subtotal for z
                        in lines])
            ht_without_carrier = inv.amount_untaxed - ht_carrier
            if ht_without_carrier<0:
                ht_carrier = ht_carrier+ht_without_carrier
                ht_without_carrier = 0.00
            inv.sub_total_ht_carrier = ht_carrier
            inv.sub_total_ht_without_carrier = ht_without_carrier
        
    
    sub_total_ht_without_carrier=fields.Float(string="Subtotal HT without carrier",
                                              compute=calc_sub_total,
                                              default=0.0
                                              )
    sub_total_ht_carrier=fields.Float(string="Subtotal HT carrier",
                                      compute=calc_sub_total,
                                      default=0.0)
        
    def _compute_delivery_carrier(self):
        for record in self:
            delivery_address = False
            if record.picking_ids:
                if len(record.picking_ids) != 0:
                    carrier_to_check = record.picking_ids[0].carrier_id
                    for picking in record.picking_ids:
                        if carrier_to_check != picking.carrier_id:
                            delivery_address = False
                            break
                    delivery_address = carrier_to_check
            if not delivery_address:
                if record.sale_order_ids:
                    if len(record.sale_order_ids) != 0:
                        carrier_to_check = (
                            record.sale_order_ids[0].carrier_id)
                        for so in record.sale_order_ids:
                            if carrier_to_check != so.carrier_id:
                                delivery_address = False
                                break
                        delivery_address = carrier_to_check
            record.carrier_id = delivery_address
            record.calc_sub_total()
