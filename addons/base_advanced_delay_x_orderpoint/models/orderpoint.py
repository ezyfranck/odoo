# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"
    
    use_expected_date = fields.Boolean(string="Use specific expected date")


    def _prepare_procurement_values(self, date=False, group=False):
        """ Prepare specific key for moves or other components that will be created from a stock rule
        comming from an orderpoint. This method could be override in order to add other custom key that could
        be used in move/po creation.
        """
        res=super(Orderpoint, self)._prepare_procurement_values( date, group)   
        
        if self.use_expected_date :
            res['date_deadline']=self.product_id._expected_date_for_qty(quantity=self.qty_to_order)
            res['date_planned']=self.product_id._expected_date_for_qty(quantity=self.qty_to_order,additionnal_delay=self.product_id.delivery_delay_quantity)
        return res 