import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    use_final_shipping_from_order = fields.Boolean(
        string="Use shipping partner from order AS final partnershipping"
    )

    order_type_id = fields.Many2one(
        string="associated order type",
        comodel_name="sale.order.type",
    )
