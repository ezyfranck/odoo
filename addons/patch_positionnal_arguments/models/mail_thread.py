# -*- coding: utf-8 -*

import logging
from odoo import _, api, fields, models
from odoo.tools import float_is_zero, float_compare
from odoo.addons import decimal_precision as dp


_logger = logging.getLogger(__name__)

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'
    
    
    @api.returns('mail.message', lambda value: value.id)
    def logistics_message_post(self, body='', 
                     message_type='notification'):
        _logger.debug("Patch for XMLRPC/JSONRPC call that can't handle positionnal argument thtough Java : https://github.com/odoo-java/odoo-java-api/issues/18")
        return self.message_post(body=body, message_type=message_type)