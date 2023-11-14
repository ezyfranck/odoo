from odoo import models,fields

class ModeleTest(models.Model):
    _name = "modele_test"   #définit le nom du modèle et le nom de la table en BDD
    _description = "test modele"
    
    name = fields.Char('Nom',default="Appt", help="Spécifier un nom")
    description = fields.Text('Description')
    postcode = fields.Char('Code postal')
    expected_price = fields.Float('Prix attendu')
    date_availability = fields.Date('Date', copy=False, default=fields.Date.today())    
    selling_price = fields.Float('Prix de vente', readonly=True, copy=False)
    bedrooms = fields.Integer('Nombre de chambre', default=2)
    living_area = fields.Integer('Surface salon')
    facades = fields.Integer('Nombre de facade')
    garage = fields.Boolean('Garage')
    garden = fields.Boolean('Jardin')
    garden_area = fields.Integer('Surface du jardin')
    garden_orientation = fields.Selection(
        string = "Orientation",
        selection = [('est','Est'),('ouest','Ouest'),('nord','Nord'),('sud','Sud')],
        help = "Choisir une orientation"
    )
    