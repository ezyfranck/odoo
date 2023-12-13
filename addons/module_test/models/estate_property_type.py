from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate_property_type"
    _description = "nouveau modèle de description des vendeurs et acheteurs"
    _order= "name"
    
    name= fields.Char("Nom", required= True)
    property_ids = fields.One2many('modele_test','property_type_id', string="Propriétés")
    sequence = fields.Integer("sequence", default=10)
    
    offer_count = fields.Integer(string="Offers Count", compute="_compute_offer")
    offer_ids = fields.Many2many("estate_property_offer", string="Offres", compute="_compute_offer")
        
    def _compute_offer(self):
        # This solution is quite complex. It is likely that the trainee would have done a search in
        # a loop.
        data = self.env["estate_property_offer"].read_group(       #self.env permet d'interagir avec la BDD. self.env['nom_du_modele']
            [("property_id.state", "!=", "canceled"), ("property_type_id", "!=", False)],     # plusieurs méthodes: pour chercher des enr spécifiques:
            ["ids:array_agg(id)", "property_type_id"],          # .search([('champ', '=', 'valeur')])  ### pour créer un nouvel enr: .create({'champ': 'valeur'})
            ["property_type_id"],               # pour mettre à jour un enr: record= self.env['modele'].browse(record_id) puis record.write ...
        )
        mapped_count = {d["property_type_id"][0]: d["property_type_id_count"] for d in data}
        mapped_ids = {d["property_type_id"][0]: d["ids"] for d in data}
        for prop_type in self:
            prop_type.offer_count = mapped_count.get(prop_type.id, 0)
            prop_type.offer_ids = mapped_ids.get(prop_type.id, [])
            
    def action_view_offers(self):
        res = self.env.ref("module_test.estate_property_offer_action").read()[0]  #fait référence à l'action estate_property_offer_action du module_test
        res["domain"] = [("id", "in", self.offer_ids.ids)]                          #ici dans la vue estate_property_offer_views  # .ref pour lecture seulement
        return res                                                                  # tandis que self.env pour CRUD. [0] premier élément de la liste
                                                                                # res['domain'] fait référence au champ domaine de la meme vue et l'expression
                                                                                # récupère tous les ids de offer_ids qui pointe vers estate_property_offer
    