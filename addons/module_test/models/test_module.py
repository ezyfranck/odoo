from odoo import api, models, fields
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class ModeleTest(models.Model):
    _name = "modele_test"   #définit le nom du modèle et le nom de la table en BDD
    _description = "test modele"
    _sql_constraints= [
        ("check_postcode", "CHECK(LENGTH(postcode) = 5)", "Veuillez sasir un code postal valide !"),
        ("check_expected_price", "CHECK(expected_price >=0)", "Le prix attendu doit être >= 0 !"),
        ("set_unique_name", "UNIQUE(name)", "Le nom donné est dèjà existant !"),
        ("check_total_area", "CHECK(total_area >=0)", "La surface du bien doit être renseignée et positive !")
        ]
    
    def action_cancel(self):
        for _ in self:
            if "cancelled" in self.mapped('state'):
                raise UserError("Un bien annulé ne peut pas être vendu")
        return self.write({'state':'sold'})
    
    def action_sold(self):
        for _ in self:
            if "sold" in self.mapped('state'):
                raise UserError("Un bien vendu ne peut pas être annulée")
        return self.write({'state':'cancelled'})
            
     
    name = fields.Char('Nom', required= True)
    description = fields.Text("Description")
    postcode = fields.Char("Code postal")
    expected_price = fields.Float("Prix attendu", required= True)
    
    ##### default method #####
    def _default_date_availability(self):
        return fields.Date.context_today(self) + relativedelta(months=3)
    ##########################
    
    # valeur par défaut de date_availability = date du jour + 3 mois 
    date_availability = fields.Date("Disponibilité", 
                                    copy=False, 
                                    default= lambda self: self._default_date_availability() 
                                    )  
       
    selling_price = fields.Float(string="Prix de vente", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Nombre de chambre", default=2)
    total_area = fields.Float(string="Superficie total (m²)", compute='_compute_total')
    living_area = fields.Integer(string="Surface salon (m²)")
    facades = fields.Integer(string="Nombre de facade")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Jardin")
    garden_area = fields.Integer(string="Surface du jardin (m²)", default=0)
    garden_orientation = fields.Selection(
        string = "Orientation",
        selection = [("nord","Nord"),("est","Est"),("sud","Sud"),("ouest","Ouest")],
        help = "Choisir une orientation"
    )
    # champ réservé - si False , le record n'apparaitra pas dans la liste
    active = fields.Boolean(string="Active", default= True)
    
    state = fields.Selection(
        string= "Statut",
        selection= [("new","Nouveau"),("offer_received","Offre reçu"),("offer_accepted","Offre accepté"),
                    ("sold","Vendu"),("cancelled","Annulé")],
        default= "new",
        required= True,
        copy= False,
        help= "Choisir un statut pour l'offre"
    )
    
    property_type_id = fields.Many2one('estate_property_type',string='Type', help="Définir le type de propriété")
    
    salesman_id= fields.Many2one('res.users', string="Vendeur", default= lambda self: self.env.user)
    buyer_id= fields.Many2one('res.partner', string="Acheteur", readonly= True, copy=False)
    
    tag_ids= fields.Many2many('estate_property_tag', string="Tags")
    offer_ids= fields.One2many('estate_property_offer','property_id', string='offres')
    best_price= fields.Integer(string='Meilleur prix', compute='_compute_best_price')
    
    @api.onchange("property_type_id")
    def _onchange_property_type_id(self):
        for record in self:
            match record.property_type_id.name:
                case 'Appartement':
                    record.facades=2
                case 'Maison':
                    record.facades=4
                case 'Commerce':
                    record.facades=1
                case _:
                    record.facades=1
            
    @api.depends("living_area","garden_area")
    def _compute_total(self):
        for area in self:
            area.total_area= area.living_area + area.garden_area
            
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price= max(record.offer_ids.mapped("price")) if record.offer_ids else 0 