import logging

from odoo import models

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _assign_picking_post_process(self, new=False):
        super(StockMove, self)._assign_picking_post_process(new=new)
        if new:
            picking_id = self.mapped("picking_id")
            if picking_id.sale_id.id and picking_id.picking_type_id.code == "outgoing":
                carrier_id = picking_id.sale_id.carrier_id
                partner_shipping_id = self.group_id.partner_id
                if (
                    carrier_id.use_final_shipping_from_order
                    and partner_shipping_id != picking_id.partner_id
                ):
                    picking_id.write(
                        {"final_shipping_partner_id": partner_shipping_id.id}
                    )
