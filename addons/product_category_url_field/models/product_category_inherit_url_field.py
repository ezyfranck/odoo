from odoo import models, fields

class ProductCategoryInherited(models.Model):
    _inherit= 'product.category'
    
    url_field= fields.Char(string="Lien du questionnaire", help="Renseigner une URL valide")
    
    