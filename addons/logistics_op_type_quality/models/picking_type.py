import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class L4StockPickingType(models.Model):
    _inherit = "l4.stock.picking.type"
    
    quality = fields.Char(string="Quality", required=True)
