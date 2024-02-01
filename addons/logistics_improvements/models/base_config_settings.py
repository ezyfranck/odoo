import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    check_product_constraints = fields.Boolean(
        string="Use controls on products fields", default=True
    )
    check_partner_constraints = fields.Boolean(
        string="Use controls on partner fields", default=True
    )


class ResConfigSetting(models.TransientModel):

    _inherit = "res.config.settings"

    check_product_constraints = fields.Boolean(
        related="company_id.check_product_constraints",
        readonly=False,
        string="Use controls on products fields",
    )
    check_partner_constraints = fields.Boolean(
        related="company_id.check_partner_constraints",
        readonly=False,
        string="Use controls on partner fields",
    )
