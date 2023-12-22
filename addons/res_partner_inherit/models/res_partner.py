from odoo import fields, models

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'
    _description = "Contact with limitation on the street field to 35 characters"
    
    street = fields.Char(size=35)