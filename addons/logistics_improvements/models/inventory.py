# -*- coding: utf-8 -*-

import time
import logging
from odoo.tools.float_utils import float_compare, float_round
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


_logger = logging.getLogger(__name__)


class StockInventoryAdjustmentName(models.TransientModel):
    _inherit = 'stock.inventory.adjustment.name'


    def flux_action_apply(self):
        passed = False
        res = self.action_apply()
        if not res:
            passed = True
        return passed