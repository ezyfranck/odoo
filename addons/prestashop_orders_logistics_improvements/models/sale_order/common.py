# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models

# from odoo.addons.logistics_improvements.models.order import SALE_DELIVERY_STATE


class SaleOrder(models.Model):
    _inherit = "sale.order"

    prestashop_order_id = fields.Integer(
        related="prestashop_bind_ids.prestashop_id",
        store=True,
        string="Order_id On prestashop",
        default=False,
        index=True,
    )

    def _compute_sale_delivery_state(self):
        # Listener are not implemented for compute method, so using classi inheritance here
        for order in self:
            initial_delivery_state = order.delivery_state
            super(SaleOrder, order)._compute_sale_delivery_state()
            new_delivery_state = order.delivery_state
            if (
                order.prestashop_bind_ids
                and initial_delivery_state != new_delivery_state
            ):
                # a quick test to see if it is worth trying to export sale state
                states = self.env["sale.order.state.list"].search(
                    [("name", "=", new_delivery_state)]
                )
                if states:
                    for binding in order.prestashop_bind_ids:
                        binding.with_delay(priority=20).export_sale_state()


class PrestashopSaleOrder(models.Model):
    _inherit = "prestashop.sale.order"


    def find_prestashop_state(self):
        self.ensure_one()
        state_list_model = self.env["sale.order.state.list"]
        state_lists = state_list_model.search([("name", "=", self.delivery_state)])
        for state_list in state_lists:
            if state_list.prestashop_state_id.backend_id == self.backend_id:
                return state_list.prestashop_state_id.prestashop_id
        return None