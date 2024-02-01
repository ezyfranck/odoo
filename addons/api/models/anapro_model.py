from odoo import models, api, fields
#from . import mapper as map

   
class GetAnapro(models.Model):
    _name= 'get.anapro'
    _description= "test anapro"
    
    partner_id = fields.Integer(string="ID Partner")
    partner_name = fields.Char(string="Nom Partner")
    partner_zip = fields.Char(string="Code Postal")
    partner_city = fields.Char(string="Ville")
    purchase_id = fields.Integer(string="ID purchase")
    carrier_id = fields.Integer(string="ID transporteur")
    carrier_name = fields.Char(string="Nom: ")
    product_qty = fields.Integer(string="Quantité attendue")
    product_name = fields.Char(string="Nom Produit")
    product_weight = fields.Float(string="Poids")
    product_default_code = fields.Char(string="Référence Interne")
    product_barcode = fields.Char(string="Code barre")
    
    @api.model
    def get_anapro_action(self):
        print("Entrée get_anapro_action")
        
        data_mapped = {}
        
        # if existing products in get.anapro purge
        existing_products= self.env['get.anapro'].search([])
        if existing_products:
            existing_products.unlink()
        
        # link to stock.picking to get info when state is assigned
        product_info = self.env['stock.picking'].search([('state', '=', 'assigned')])
        
        print("*"*175, "\n")        
        for product in product_info:
            # if product is Purchase(P) state and name set to 'WH/IN/'
            if product.origin[0] == 'P' and product.name[0:6] == 'WH/IN/':
                
                #get id purchase
                id_purchase = int(product.origin[1:].lstrip('0'))
                
                #link to partner to get id, name, zip and city
                partner = self.env['res.partner'].search([('id', '=', int(product.partner_id))])
                partner_id = partner.id
                partner_name = partner.name
                partner_zip = partner.zip
                partner_city = partner.city
                
                #link to purchase.order with id purchase
                purchase_order = self.env['purchase.order'].search([('id', '=', id_purchase)])
                purchase_id = int(purchase_order.id)
                
                #get carrier_id from stock.picking and link to delivery.carrier to get name
                carrier_id = int(product.carrier_id)
                carrier = self.env['delivery.carrier'].search([('id', '=', carrier_id)])
                carrier_name = carrier.name
                
                # link to purchase.order.line with order_id
                purchase_order_line_info = self.env['purchase.order.line'].search([('order_id', '=', purchase_id)])
                for purchase in purchase_order_line_info:
                    
                    if purchase.state == 'purchase':
                    
                        product_qty = purchase.product_qty  
                        product_product = self.env['product.product'].search([('id', '=', int(purchase.product_id))])   
                        product_default_code = product_product.default_code
                        product_barcode = product_product.barcode
                        product_name = product_product.name
                        product_weight = product_product.weight
                                            
                        data_mapped= {
                            'partner_id': partner_id,
                            'partner_name': partner_name,
                            'partner_zip': partner_zip,
                            'partner_city': partner_city,
                            'purchase_id': id_purchase,
                            'carrier_id': carrier_id,
                            'carrier_name': carrier_name,
                            'product_qty': product_qty,
                            'product_default_code': product_default_code,
                            'product_barcode': product_barcode,
                            'product_name': product_name,
                            'product_weight': product_weight,
                        }
                    
                        print("Data_mapped", data_mapped)
                        print("*"*175, "\n")
                        
                        # if data recording data in DB
                        if data_mapped:
                            print("data is true")
                            self.create(data_mapped)
 
        return True           