# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    # TODO: Waiting for answer from the customer if this delay \
    # is integrated in the delay
    supplier_reliability_delay = fields.Integer(
        string="Supplier reliability",
        help="""This field has the same purpose as
        the general parameter on company in days""",
    )
