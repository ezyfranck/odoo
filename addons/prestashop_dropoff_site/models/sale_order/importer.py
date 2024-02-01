# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import pytz
from odoo import _, fields
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.queue_job.exception import FailedJobError, NothingToDoJob
from odoo.addons.connector_ecommerce.components.sale_order_onchange import (
    SaleOrderOnChange,
)

from datetime import datetime, timedelta
from decimal import Decimal
import logging
from re import search
_logger = logging.getLogger(__name__)

try:
    from prestapyt import PrestaShopWebServiceError
except:
    _logger.debug('Cannot import from `prestapyt`')



class SaleOrderImportMapper(Component):
    _inherit = 'prestashop.sale.order.mapper'


    @mapping
    def mondial_relay(self, record):
        values={}
        if 'mr_relay_number' in record:
            values.update({"mr_relay_number": basename})
        return values
    