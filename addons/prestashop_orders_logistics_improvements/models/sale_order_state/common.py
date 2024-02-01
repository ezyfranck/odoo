# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models

# from odoo.addons.logistics_improvements.models.order import SALE_DELIVERY_STATE


class SaleOrderStateList(models.Model):
    _inherit = "sale.order.state.list"

    @api.model
    def _get_sale_order_states(self):
        return self.env["sale.order"]._fields["delivery_state"].selection

    name = fields.Selection(
        selection=_get_sale_order_states,
        string="Odoo Delivery State",
        required=True,
    )
