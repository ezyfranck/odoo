# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    
    name_l4 = fields.Char(string='Nom1 pour Logistique')
    name_l4_key2 = fields.Char(string='Nom2 pour Logistique')
    
    name = fields.Char(string='Name', required=True)