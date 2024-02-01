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
_logger = logging.getLogger(__name__)


class AddressImportMapper(Component):
    _inherit = 'prestashop.address.mappper'
    _apply_on = 'prestashop.address'

    @mapping
    def name(self, record):
        parts = [record['firstname'], record['lastname']]
        name = ' '.join(p.strip() for p in parts if p.strip())
        _logger.info('Do not use alias in the mapping')
        return {'name': name}
