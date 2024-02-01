from odoo import fields, models

class ProductTemplateImagesInherited(models.Model):
    _inherit= 'product.template'
    
    product_images_ids= fields.Many2many('ir.attachment', string="Images produit")
    
    
     