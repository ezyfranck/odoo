from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate_property_tag"
    _description = "Tag de description des biens immobilier"
    _order = "name"
    
    name = fields.Char('Nom', required=True)
    color = fields.Integer("Color Index")  #color index est un index numérique des couleurs assigné à color
    