from odoo import fields, models

class ProductTemplateSerialSupplier(models.Model):
    _inherit= 'product.template'
    
    ref_supplier= fields.Char(string="Référence fournisseur")
    ean_supplier= fields.Char(string="EAN fournisseur", size=13)
    