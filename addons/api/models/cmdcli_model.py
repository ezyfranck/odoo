from odoo import models, api, fields
#from . import mapper as map

   
class GetCmdcli(models.Model):
    _name= 'get.cmdcli'
    _description= "test cmdcli"
    
    activityCode = fields.Char(string="Code activité")
    activityName= fields.Char(string="Nom de l'activité")
    orderUniqueID= fields.Char(string="Stock picking name")
    customerOrderID= fields.Char(string="Client order Ref")
    prepOrderGroupID= fields.Integer(string="order group id")
    commandChannelDescription= fields.Char(string="command description")
    commandType= fields.Char(string="command type")
    doManagedCustomerNumber= fields.Char(string="custom number")
    deliveryAddressLastname= fields.Char(string="nom adresse livraison")
    deliveryAddressCompany= fields.char(string="compagnie adresse livraison")
    deliveryAddressAddress1= fields.Char(string="adresse 1 livraison")
    deliveryAddressAddress2= fields.Char(string="adresse 2 livraison")
    '''
    deliveryAddressPostalCode=
    deliveryAddressCity=
    deliveryAddressCountry=
    deliveryAddressPhone=
    deliveryAddressEmail=
    customerInvoiceNumber=
    paymentCurrency=
    totalInvoiceHT=
    intracommunityVATNumber=
    transportCode=
    transportServiceCode=
    deliveryPickupPointID=
    pickupPointCountryCode=
    documentLanguage=
    '''

    
    partner_id = fields.Integer(string="ID Partner")
    partner_name = fields.Char(string="Nom Partner")
    partner_zip = fields.Char(string="Code Postal")
    partner_city = fields.Char(string="Ville")
    carrier_id = fields.Integer(string="ID transporteur")
    carrier_name = fields.Char(string="Nom: ")
    sale_qty = fields.Integer(string="Quantité attendue")
    product_name = fields.Char(string="Nom Produit")
    product_weight = fields.Float(string="Poids")
    product_default_code = fields.Char(string="Référence Interne")
    product_barcode = fields.Char(string="Code barre")
    
    @api.model
    def get_cmdcli_action(self):
        
        print("Entrée get_cmdcli_action")
        
        data_mapped = {}
        
        # check existing products in get.cmdcli and purge
        existing_products= self.env['get.cmdcli'].search([])
        if existing_products:
            existing_products.unlink()
                    
        # link to stock.picking to get info when state is assigned
        stock_info = self.env['stock.picking'].search([('state', '=', 'assigned')])
        
        print("*"*175, "\n")        
        for stock in stock_info:
            # if product is Sale(S) state and name set to 'WH/OUT/'
            if stock.origin[0] == 'S' and stock.name[0:7] == 'WH/OUT/':
                
                orderUniqueID= stock.name
                order_id= stock.name[7:len(stock.name)]
                customer_Order_ID= self.env['sale.order'].search([('name','=',order_id)])
                for record in customer_Order_ID:
                    customerOrderID= record.client_order_ref
                    prepOrderGroupID= stock.group_id
                    
                    commandChannelDescription= stock.canal
                    commandType= stock.canal
                    doManagedCustomerNumber= record.client_order_ref
                    
                    deliveryAddressLastname= record.name
                    ####
                    
                    

                    
                    

                                              
                #link to partner to get id, name, zip and city
                partner = self.env['res.partner'].search([('id', '=', int(stock.partner_id))])
                partner_id = partner.id
                partner_name = partner.name
                partner_zip = partner.zip
                partner_city = partner.city
                
                #get carrier_id from stock.picking and link to delivery.carrier to get name
                carrier_id = int(stock.carrier_id)
                carrier = self.env['delivery.carrier'].search([('id', '=', carrier_id)])
                carrier_name = carrier.name
                
                # link to sale.order.line with order_id
                sale_order_line_info = self.env['sale.order.line'].search([('order_id', '=', int(stock.sale_id))])
                for sale in sale_order_line_info:
                    
                    if sale.state == 'sale':
                        # get sale quantity and link to product.product to get info on product
                        sale_qty = sale.qty_delivered 
                        sale_sale = self.env['product.product'].search([('id', '=', int(sale.product_id))])   
                        product_default_code = sale_sale.default_code
                        product_barcode = sale_sale.barcode
                        product_name = sale_sale.name
                        product_weight = sale_sale.weight
                        
                        # map data
                        data_mapped= {
                            'partner_id': partner_id,
                            'partner_name': partner_name,
                            'partner_zip': partner_zip,
                            'partner_city': partner_city,
                            'carrier_id': carrier_id,
                            'carrier_name': carrier_name,
                            'sale_qty': sale_qty,
                            'product_default_code': product_default_code,
                            'product_barcode': product_barcode,
                            'product_name': product_name,
                            'product_weight': product_weight,
                        }
                        
                        print("Data_mapped", data_mapped)
                        print("*"*175, "\n")
                        
                        # id data recording in DB
                        if data_mapped:
                            print("data is true")
                            self.create(data_mapped)
        return True