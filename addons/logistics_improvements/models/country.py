import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResCountry(models.Model):
    _inherit = "res.country"

    l4_export_invoices = fields.Boolean(
        string="Export Associated Invoices", default=False
    )
