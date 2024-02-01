# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime as datetime_package
import logging
from datetime import datetime, timedelta

from odoo import fields, models
from odoo.addons import decimal_precision as dp
from odoo.fields import first
from odoo.tools import parse_date

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_values(self, group_id=False):

        self.ensure_one()
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        values.update({
                'team_id': self.order_id.team_id.id or False
            })
        return values