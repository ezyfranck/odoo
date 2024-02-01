# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SaleWorkflowProcess(models.Model):
    _inherit = "sale.workflow.process"

    prestashop_partner_category = fields.Many2many(
        comodel_name="prestashop.res.partner.category"
    )
