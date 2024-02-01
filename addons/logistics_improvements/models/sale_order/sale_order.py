import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

SALE_DELIVERY_STATE = [
    # ('sent_to_logistics',	'Sent to logistics'),
    ("refused_by_logistics", "Refused by logistics"),
    ("preparation_to_do", "Preparation to do(Accepted by Logistics)"),
    ("cancelled_by_logistics", "Cancelled by logistics"),
    ("preparation_in_progress", "Preparation in progress"),
    ("preparation_done", "Preparation Done!"),
    ("waiting_for_shipping", "Waiting for shipping"),
    # ('shipped',	'Shipped'),
    # ('delivered',	'Delivered'),
]


IDCANAL = [
    ("WEB", "WEB"),
    ("PRO", "PRO"),
    ("MARKETPLACE", "MARKETPLACE"),
    ("DISTRIBUTEUR", "DISTRIBUTEUR"),
    ("REASSORT", "REASSORT"),
    ("SPECIAL", "SPECIAL"),
]


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        partner_shipping_id = self.env["res.partner"]
        if "partner_shipping_id" in vals and vals["partner_shipping_id"]:
            partner_shipping_id = self.env["res.partner"].browse(
                [vals["partner_shipping_id"]]
            )
        vals = self._logistics_infos_vals(partner_shipping_id, vals)
        res = super(SaleOrder, self).create(vals)
        return res

    def _logistics_infos_vals(self, partner_shipping_id, vals):
        # TODO: migrate this method in partner to return a json to have better factoring
        vals_from_partner = {
            "idcanal": partner_shipping_id.idcanal,
            "typecmd": partner_shipping_id.typecmd,
            "idgroup": partner_shipping_id.idgroup,
        }
        vals_from_partner.update(vals)
        return vals_from_partner

    @api.onchange("partner_shipping_id")
    @api.depends("partner_shipping_id")
    def onchange_logistics_info(self):
        vals = self._logistics_infos_vals(self.partner_shipping_id, {})
        self.idcanal = vals["idcanal"]
        self.typecmd = vals["typecmd"]
        self.idgroup = vals["idgroup"]

    fully_delivered = fields.Boolean(
        related="all_qty_delivered", copy=False, store=True
    )

    delivery_status = fields.Selection(
        selection_add=SALE_DELIVERY_STATE,
    )

    def _is_picking_in_logistic_state(self):
        """
        if an error occurs in logistics, it should be the main information,
        otherwise picking states 'sent' and 'preparation' could be merged as
        an indication for sales team.

        Returns:
            _type_: False or the locgistics state
        """
        self.ensure_one()
        logistics_pickings = self.picking_ids.filtered(
            lambda p: p.textual_substate in list(zip(*SALE_DELIVERY_STATE))[0]
        )

        if any(
            self.picking_ids.filtered(
                lambda p: p.textual_substate in ["refused_by_logistics"]
            )
        ):
            return "refused_by_logistics"

        if any(
            self.picking_ids.filtered(
                lambda p: p.textual_substate in ["cancelled_by_logistics"]
            )
        ):
            return "cancelled_by_logistics"

        if len(logistics_pickings) > 0:
            states = logistics_pickings.mapped("textual_substate")
            return states[-1]
        return False

    @api.depends('order_line.qty_delivered','picking_ids', 'picking_ids.state','picking_ids.textual_substate')
    def _compute_delivery_status(self):
        for order in self:
            if not order._is_picking_in_logistic_state():
                super(SaleOrder, order)._compute_delivery_status()
            else:
                order.delivery_status = order._is_picking_in_logistic_state()

    idcanal = fields.Selection(
        selection=IDCANAL, string="IDCANAL (Logistics)", index=True
    )
    typecmd = fields.Char(string="Type Commande (Logistics)")
    idgroup = fields.Char(string="IDGROUP (Logistics)")
