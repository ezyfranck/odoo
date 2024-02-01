import json
from odoo import models, api, fields
from . import mapper as map
from . import api_connect as APC
from . import client_model as CLI
   
class GetProduct(models.Model):
    _name= 'get.product'
    _description= "test refart"
    
    activityCode = fields.Char(string="Code activité")
    activityName= fields.Char(string="Nom de l'activité")
    articleReference= fields.Char(string="Référence interne")
    longArticleDescription= fields.Char(string="Longue description")
    shortArticleDescription= fields.Char(string="Courte description")
    netWeightPerUVC= fields.Integer(string="Poids net UVC")
    grossWeightPerUVC= fields.Integer(string="Poids")
    articleAnalysisCode= fields.Char(string="Code Analyse")
    barcodes= fields.Char(string="Barcode")
    articleType = fields.Char(string="Type article")
    barcodeUnit= fields.Char(string="unité Codbar")
    isPrimary= fields.Boolean(string="Primaire")
    nomenclatureManaged= fields.Boolean(string="Nomenclature")
    articlePrice1= fields.Integer(string="Prix")
    barcodeQuantity= fields.Char(string="Quantité codbar")

    def connect_to_api(self, secret, trigramme, ident):
        # API ezyConnect connection
        print(f"secret: {secret} trigramme: {trigramme} reçu dans refart_model ! \nconnection à l'API !")
        conn = APC.APIConnect.connect(secret, ident)
        print(f"token OAuth recupéré dans connect_to_api: {conn} \nEnregistrement dans le self")
        
        global api_token, api_trigramme
        api_trigramme= trigramme
        api_token= conn
            
    def get_product_action(self):
        # initialization data_mapped dict
        data_collected = {}
        print("Entrée dans get_product_action")
        print(f"Controle du token et trigramme dans le self !")
        print(api_token, "//", api_trigramme)
        
        # token_access is true
        if api_token:
            print("Token récupéré !")
            print("-"*150)

            # check existing products in get.product and purge 
            existing_products= self.env['get.product'].search([])
            if existing_products:
                existing_products.unlink()
            
            # get all products in product.product
            product_info= self.env['product.product'].search([])
            
            # for each product
            for product in product_info:    
                
                articleType= product.product_tmpl_id.detailed_type
                #filter active product and product product and product consume
                if product.active == True and articleType in ['product', 'consu']:
                    # get products
                    articleReference= product.default_code
                    longArticleDescription = product.name 
                    shortArticleDescription = product.name                                   
                    barcodes= product.barcode
                    articlePrice1= product.list_price * 1000
                    articleAnalysisCode= "E"
                    nomenclatureManaged= self.env['mrp.bom'].search([('product_id', "=", product.id)])
                    if nomenclatureManaged.product_qty > 0:
                        nomenclatureManaged= True
                    else:
                        nomenclatureManaged= False
                    netWeightPerUVC= 0
                    grossWeightPerUVC= 0
           
                    #compose list data dict and send to mapper       
                    data_collected= [
                        {
                        "activityCode": api_trigramme,
                        "activityName": api_trigramme, 
                        "articleReference": articleReference,
                        "longArticleDescription": longArticleDescription,
                        "shortArticleDescription": shortArticleDescription,
                        "articleType": 0,
                        "nomenclatureManaged": nomenclatureManaged,
                        "netWeightPerUVC": netWeightPerUVC,   
                        "grossWeightPerUVC": grossWeightPerUVC, 
                        "articlePrice1": int(articlePrice1),       
                        "articleAnalysisCode": articleAnalysisCode,
                        "barcodes": [
                            {
                                "code": barcodes,
                                "isPrimary": True,
                                "barcodeUnit": "UVC",
                                "barcodeQuantity": 1 
                            }]
                        }
                    ]
                    print("DATAS COLLECTED: ",data_collected)
                    try:
                        # serialize data_collected and send to mapper
                        json_data = json.dumps(data_collected, indent=2)
                        print("Envoi des données au MAPPER")                    
                        map.DataMapper.map_product_data("REFART", api_token, json_data) 
                    except TypeError as e:
                        print(f"Error during JSON serialization: {e}")
        
                    # recording data dict in DB
                    if data_collected:
                        #data_collected= json.loads(data_collected)    # becareful DB for barcodes field
                        self.create(data_collected)
                        print("# data enregistrées en BDD")
                        print("*"*150)

            return True
        else:
            raise noConnection("Problème de connexion à l'API EzyConnect !")

    
class noConnection(Exception):
    pass