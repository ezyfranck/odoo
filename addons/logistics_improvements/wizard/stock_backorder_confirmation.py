# -*- coding: utf-8 -*-

import time
import logging
from odoo.tools.float_utils import float_compare, float_round
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


_logger = logging.getLogger(__name__)


from odoo import api, fields, models, _


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process_logistic(self):
        self.with_context(button_validate_picking_ids=self.pick_ids.ids).process()
        return True

    def process_cancel_backorder_logistic(self):
        self.with_context(button_validate_picking_ids=self.pick_ids.ids).process_cancel_backorder()
        return True
        
        