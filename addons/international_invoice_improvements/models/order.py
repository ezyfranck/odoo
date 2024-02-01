# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError
from functools import *

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("order_line", "carrier_id")
    def calc_sub_total(self):
        for order in self:
            order.sub_total_ht_carrier = 0.0
            lines = order.order_line.filtered(
                lambda r: r.product_id == order.carrier_id.product_id
            )
            if order.order_line and len(lines) > 0:
                order.sub_total_ht_carrier = reduce(
                    lambda x, y: x + y, [z.price_subtotal for z in lines]
                )
            order.sub_total_ht_without_carrier = (
                order.amount_untaxed - order.sub_total_ht_carrier
            )

    sub_total_ht_without_carrier = fields.Float(
        string="Subtotal HT without carrier",
        compute=calc_sub_total,
        #                                             store=True,
        default=0.0,
    )
    sub_total_ht_carrier = fields.Float(
        string="Subtotal HT carrier",
        compute=calc_sub_total,
        #                                       store=True,
        default=0.0,
    )

    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super()._create_invoices(grouped=grouped, final=final, date=date)

        for inv in self:
            inv.calc_sub_total()
        return res
