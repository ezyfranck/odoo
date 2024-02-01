from ast import Store
from types import new_class
from odoo import fields, models, api
from odoo.exceptions import ValidationError

class GetClient(models.Model):
    _name= "get.client"
    _description= "test get client"
    _auto= False
    
    trigramme = fields.Selection(string="Code activité",
                                    selection=[('ODO','ODO'), ('TSF','TSF'), ('WAJ','WAJ'),
                                               ('MAI','MAI'), ('HER','HER'), ('BDR','BDR'), 
                                               ('BRS','BRS'), ('JAD','JAD'), ('JUL','JUL'), 
                                               ('KYS','KYS'), ('LIN','LIN'), ('LAZ','LAZ'),
                                               ('REJ','REJ'), ('LSF','LSF'), ('ORP','ORP'),
                                               ('SOU','SOU'), ('VOL','VOL'), ('AKA','AKA')],
                                    required=True, default= '')
    
    ident= fields.Char(string="Identifiant", readonly=True, default= '')
    client_label= fields.Char(string="Nom du client", default= '', readonly=True)
    activity_name= fields.Char(string="Nom de l'activité", default= '', readonly=True)
    client_secret= fields.Char(string="Secret", default= '', readonly=True)
            
    @api.onchange('trigramme')
    def _set_activity_name(self):
        # if trigramme exists fill readonly fields
        existing_record= self.env['set.client'].search([('trigramme', '=', self.trigramme)])
        if existing_record:
            for info in existing_record:
                self.ident= info.ident
                self.client_label= info.client_label
                self.activity_name= info.activity_name
                self.client_secret= info.client_secret
                val2= self.trigramme
            
            # send secret, trigramme and name to refart_model , connect_to_api method    
            model_refart_obj= self.env['get.product']
            print("Client sélectionné !")
            print(f"envoi secret: {self.client_secret} trigramme: {self.trigramme} et name: {val2} à refart_model !")
            model_refart_obj.connect_to_api(self.client_secret, self.trigramme, self.ident)
            

class SetClient(models.Model):
    _name= "set.client"
    _description= "test set client"
    
    ident= fields.Char(string="Identifiant", required=True, default= '')
    trigramme= fields.Char(string="Trigramme client", default= '')
    client_label= fields.Char(string="Nom du client", default= '')
    activity_name= fields.Char(string="Nom activité", default= '')
    client_secret= fields.Char(string="Secret client", default= '') 
        
    @api.onchange('ident')
    def _set_trigramme_and_name(self):
        # fill readonly fields with ident formatted XXX.xxx
        val1= self.ident[0:3].upper()
        self.trigramme= val1
        self.activity_name= val1
        
    @api.constrains('ident')
    def _check_unique_ident(self):
        # check if ident already exists
        for record in self:
            existing_client = self.search([('ident', '=', record.ident), ('id', '!=', record.id)])
            if existing_client:
                raise ValidationError("Ce code activité existe déjà !")
        
    @api.model
    def create(self, vals):
        # save data to model
        new_client= super(SetClient, self).create(vals)
        return new_client

