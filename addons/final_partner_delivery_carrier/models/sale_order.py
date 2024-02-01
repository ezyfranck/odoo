import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("partner_id", "company_id", "carrier_id")
    def _compute_sale_type_id(self):
        orders_without_type_on_carrier = self.filtered(
            lambda s: not s.carrier_id.id or not s.carrier_id.order_type_id.id
        )
        orders_with_type_on_carrier = self - orders_without_type_on_carrier

        super(SaleOrder, orders_without_type_on_carrier)._compute_sale_type_id()

        for record in orders_with_type_on_carrier:
            sale_type = record.carrier_id.order_type_id
            if sale_type.id:
                record.type_id = sale_type
                record.onchange_type_id()
