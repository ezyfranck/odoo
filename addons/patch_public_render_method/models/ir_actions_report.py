# -*- coding: utf-8 -*

import logging
from odoo import _, api, fields, models
from odoo.tools import float_is_zero, float_compare
from odoo.addons import decimal_precision as dp


_logger = logging.getLogger(__name__)

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'
    
    def render(self,report_ref, res_ids, data=None):
        _logger.debug("Make render method public again : https://github.com/odoo/odoo/issues/78528")
        return self._render(report_ref,res_ids, data)