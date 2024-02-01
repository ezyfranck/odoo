# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class PrestashopResPartnerCategory(models.Model):
    _inherit = "prestashop.res.partner.category"

    taxes_included = fields.Boolean(string="Use tax included prices")

    def create(self, vals):
        res = super().create(vals)
        res.taxes_included = res.backend_id.taxes_included
        return res
