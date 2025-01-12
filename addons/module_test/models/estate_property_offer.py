from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class EstatePropertyOffer(models.Model):
    _name = "estate_property_offer"
    _description= "Offres des biens immobiliers"
    _order = "price desc"
    _sql_constraints= [('check_positive_amount', 'CHECK(price >=0)', "Le montant de l'offre doit être > 0")]
    
    def action_accept(self):
        for record in self:
            if "accepted" in self.mapped('state'):
                raise UserError("L'offre ne peut être acceptée si le bien est déja vendu")
        return self.write({'state': 'accepted'})
    
    def action_refuse(self):
        for record in self:
            if "refused" in self.mapped('state'):
                raise UserError("L'offre ne peut être annulée si elle est annulée")
        return self.write({'state': 'refused'})
    
    price = fields.Float('Prix', required=True)
    state = fields.Selection(string='statut', 
                             selection=[('accepted','Accepté'),('refused','Refusé')], 
                             copy=False,
                             default=False)
    partner_id = fields.Many2one('res.partner', string='Client', required=True)
    property_id = fields.Many2one('modele_test', string='Propriété', required=True)
    
    validity= fields.Integer(string="Validité (jours)", default=7)
    date_deadline= fields.Date(string="Date d'échéance", compute="_date_deadline", inverse="_inverse_date_deadline")
    property_type_id = fields.Many2one('estate_property_type', related='property_id.property_type_id', string='Type de propriété', store=True)
    
    @api.depends('create_date','validity')
    def _date_deadline(self):
        for offer in self:
            # verif si date de creation de l'offre présente sinon prendre date du jour
            deadline= offer.create_date.date() if offer.create_date else fields.Date.today() 
            # ajout de la valeur (defaut 7 jours) à la date de création
            offer.date_deadline= deadline + relativedelta(days=offer.validity)  
            
    def _inverse_date_deadline(self):
        for offer in self:
            deadline= offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.validity= (offer.date_deadline - deadline).days
            
    @api.constrains('date_deadline')
    def _check_date_deadline(self):
        for record in self:
            if record.date_deadline < fields.Date.today():
                raise ValidationError("La date d'échéance ne peut être définie dans le passé !")