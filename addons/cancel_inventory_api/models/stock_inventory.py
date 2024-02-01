# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class Inventory(models.Model):
    _inherit = "stock.inventory"

    def action_cancel_draft(self):
        super(Inventory, self).action_cancel_draft()
        return True
    
    def action_done(self):
        self._action_done()
        return True

    
