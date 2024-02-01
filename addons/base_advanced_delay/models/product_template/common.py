# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends("product_variant_ids")
    def _compute_template_delays(self):
        for tmpl in self:
            if not len(tmpl.product_variant_ids) > 0:
                tmpl.update(
                    {
                        "delivery_delay_auto": False,
                        "delivery_delay_text": _("later"),
                        "delivery_delay_quantity": 0,
                        "delivery_delay_date": "2100-01-01",
                    }
                )
            else:
                prod = tmpl.product_variant_ids[0]
                tmpl.update(
                    {
                        "delivery_delay_auto": prod.delivery_delay_auto,
                        "delivery_delay_text": prod.delivery_delay_text,
                        "delivery_delay_quantity": prod.delivery_delay_quantity,
                        "delivery_delay_date": prod.delivery_delay_date,
                    }
                )

    delivery_delay_auto = fields.Boolean(
        "Auto compute the text", compute="_compute_template_delays"
    )
    delivery_delay_text = fields.Char(
        string="Text Delay for product",
        translate=True,
        compute="_compute_template_delays",
    )
    delivery_delay_quantity = fields.Float(
        "Computed Quantity for delivery text info",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_template_delays",
    )
    delivery_delay_date = fields.Date(
        "Computed date for delivery text info",
        compute="_compute_template_delays",
    )
