from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate_property_type"
    _description = "nouveau modèle de description des vendeurs et acheteurs"
    _order= "name"
    
    name= fields.Char("Nom", required= True)
        
    
    