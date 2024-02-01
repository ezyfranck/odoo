from odoo import fields, models, api

class ProductTemplateInherited(models.Model):
    _inherit= 'product.template'
    
    concat_url_field= fields.Char(string="Lien du questionnaire", compute="_compute_url_field", readonly=True, default="Non renseigné")
    
    @api.depends('categ_id.url_field','default_code')
    def _compute_url_field(self):
        for record in self:
            base_url= record.categ_id.url_field
            default_code= record.default_code
            record.concat_url_field= f"{base_url}{default_code}"
    