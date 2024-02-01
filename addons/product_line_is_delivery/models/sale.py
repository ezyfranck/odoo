# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class Inventory(models.Model):
    _inherit = "sale.order.line"

    def _is_delivery(self):
        self.ensure_one()
        if self.product_id and self.product_id.type=='service': 
            if self.is_delivery!=True:
                self.is_delivery =True
        return self.is_delivery
    
