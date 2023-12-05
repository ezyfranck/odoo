#!/usr/bin/python3
# @Time    : 29/11/2023
# @Author  : Kevin Kong (kfx2007@163.com)

from datetime import datetime as dt

from odoo import fields, models, api
import pika
import logging
import json
import datetime
#from six.moves import urllib
import urllib

_logger = logging.getLogger(__name__)


class RabbitmqParameters(models.Model):
    _name = "rabbitmq.parameters"
    _description = "Rabbit MQ parameters"

    name = fields.Char(string='name')
    active = fields.Boolean(string='active')
    rbq_user_new = fields.Char(string='User')
    rbq_exchange_new = fields.Char(string='Exchange')
    rbq_password_new = fields.Char(string='Password')
    rbq_host_new = fields.Char(string='Host')
    rbq_port_new = fields.Char(string='Port')
    rbq_message_new = fields.Char(string='message')
    rbq_trigram_new = fields.Char(string='Trigram')


class AutomatedRabbitmqSever(models.Model):
    _name = "stock.picking"
    _description = "Automate Rabbit MQ server"
    _inherit = "stock.picking"

    rbq_user_new = fields.Char(compute='_compute_rbq_user', string="User")
    rbq_exchange_new = fields.Char(compute='_compute_rbq_user', string="Exchange")
    rbq_password_new = fields.Char(compute='_compute_rbq_user', string="Password")
    rbq_host_new = fields.Char(compute='_compute_rbq_user', string="Host")
    rbq_port_new = fields.Char(compute='_compute_rbq_user', string="Port")
    rbq_trigram_new = fields.Char(compute='_compute_rbq_user', string="Trigram")
    rbq_event_status_new = fields.Char(string='Event Status', default='order-transmit', compute='_onchange_status', store=True)
    rbq_new_status_new = fields.Char(string='New Status', default='order-transmit-success', compute='_onchange_status', store=True)

    #
    #
    @api.depends('state')
    def _onchange_status(self):
        for rec in self:
            if rec.state in ['cancel']:
                rec.rbq_event_status_new = 'order-cancel'
                rec.rbq_new_status_new = 'order-transmit-failure'

            else:
                rec.rbq_event_status_new = 'order-transmit'
                rec.rbq_new_status_new = 'order-transmit-success'

    """
    These Function used to compute information  from  rabbit MQ parameters :
    """

    def _compute_rbq_user(self):
        Rabbits = self.env['rabbitmq.parameters'].search([('active', '=', True)], limit=1)

        for rec in Rabbits:
            self.rbq_user_new = str(rec.rbq_user_new)
            self.rbq_exchange_new = str(rec.rbq_exchange_new)
            self.rbq_password_new = str(rec.rbq_password_new)
            self.rbq_host_new = str(rec.rbq_host_new)
            self.rbq_port_new = str(rec.rbq_port_new)
            self.rbq_trigram_new = str(rec.rbq_trigram_new)

    def get_attribute_data(self, attribute_value="", attribute_name=""):
        res = ""
        try:
            if hasattr(self, attribute_value):
                if attribute_name != "":
                    if attribute_value == "carrier_id":
                        res = self.carrier_id.__getattribute__(attribute_name)
                    elif attribute_value == "sale_id":
                        res = self.sale_id.__getattribute__(attribute_name)
                    elif attribute_value == "partner_id":
                        res = self.partner_id.__getattribute__(attribute_name)
                    elif attribute_value == "global_channel_id":
                        res = self.global_channel_id.__getattribute__(attribute_name)
                    elif attribute_value == "picking_type_id":
                        res = self.picking_type_id.__getattribute__(attribute_name)
                    else:
                        _logger.info("\n\nGet parameters :")

                else:
                    res = self.__getattribute__(attribute_value)
            if isinstance(res, dt):
                res = res.isoformat()
        except Exception as err:
            _logger.error("\n\nError in get attribute", str(attribute_name), " : ", str(err), " - RabbitMQ Odoo V16")
        return res

    def get_attribute_data(self, attribute_value="", attribute_name=""):
        res = ""
        try:
            if hasattr(self, attribute_value):
                if self.__getattribute__(attribute_value):
                    res = self.__getattribute__(attribute_value)
                    if attribute_name != "":
                        res = res.__getattribute__(attribute_name)
            if hasattr(res, "name"):
                res = res.__getattribute__("name")
            if isinstance(res, dt):
                res = res.isoformat()
        except Exception as err:
            _logger.error("\n\nError in get attribute", str(attribute_name), " : ", str(err), " - RabbitMQ Odoo V16")

        return res

    def get_picking_line_data(self):
        """
        Get data line of picking
        return dict of dict
        """
        result = list()
        try:
            for ln in self.move_ids_without_package:
                res = dict()
                res["product-sku"] = str(ln.product_id.default_code)
                res["product-name"] = str(ln.product_id.name)
                res["product-qty"] = str(ln.product_uom_qty)
                res["product-barcode"] = str(ln.product_id.barcode)
                res["product-origin"] = str(ln.location_id.name)
                res["product-destination"] = str(ln.location_dest_id.name)
                result.append(res)
        except Exception as err:
            _logger.error("\n\nError in get picking line data : ", str(err), " - RabbitMQ Odoo V16")
        return result

    def get_instance_ecommerce(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if hasattr(self, 'shopify_instance_id'):
            try:
                if self.shopify_instance_id:
                    ecommerce_id = str(self.shopify_instance_id.id)
                    parsed_url = urllib.parse.urlparse(self.shopify_instance_id.shopify_host)
                    desired_part = parsed_url.netloc.split('.myshopify')[0]
                    desired_part ="https://admin.shopify.com/store/" + desired_part
                    ecommerce_url = str(desired_part)
                else:
                    ecommerce_id = "Odoo"
                    ecommerce_url = base_url
            except Exception :
                ecommerce_id = "Odoo"
                ecommerce_url = base_url
        elif hasattr(self, 'woo_instance_id'):
            try:
                if self.woo_instance_id:
                    ecommerce_id = str(self.woo_instance_id.id)
                    ecommerce_url = str(self.woo_instance_id.host)
                else:
                    ecommerce_id = "Odoo"
                    ecommerce_url = base_url
            except:
                ecommerce_id = "Odoo"
                ecommerce_url = base_url
        else:
            try:
                if self.sale_id:
                    if hasattr(self.sale_id, 'prestashop_bind_ids'):
                        presta_record = self.sale_id.prestashop_bind_ids
                        presta_record = presta_record[0]

                        ecommerce_id = str(presta_record.backend_id.id)
                        ecommerce_url = str(presta_record.backend_id.location)
                    else:
                        ecommerce_id = "Odoo"
                        ecommerce_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                elif self.origin:
                    sale_order = self.env['sale.order'].search([('name', '=', self.origin)])
                    if hasattr(sale_order, 'prestashop_bind_ids'):
                        presta_record = sale_order.prestashop_bind_ids
                        presta_record = presta_record[0]

                        ecommerce_id = str(presta_record.backend_id.id)
                        ecommerce_url = str(presta_record.backend_id.location)
                    else:
                        ecommerce_id = "Odoo"
                        ecommerce_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                else:
                    ecommerce_id = "Odoo"
                    ecommerce_url = base_url
            except:
                ecommerce_id = "Odoo"
                ecommerce_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return ecommerce_id, ecommerce_url

    def run_publish(self, exchange=rbq_exchange_new,
                    routing_key="", user=rbq_user_new, password=rbq_password_new,
                    host=rbq_host_new, port=rbq_port_new, trigram=rbq_trigram_new, eshop_id="",
                    eshop_url="", delivery="", origin="", message=""):

        """
        Function to publish information to rabbit MQ as:
            "name": "delivery",
            "event-name": "order-payment",
            "new-state": "order-payment-success",
            "context": "TRIGRAMME",
            "source": 'odoo',  [Previous line repeated 936 more times]
RecursionError: maximum recursion depth exceeded while calling a Python object

            "subject-id": "BL_NUMBER",
            "url": "Instance of Shopify"
        host : url of RabbitMQ Server
        port : integer
        exchange : channel
        exchange_type : type of channel : header, ...
        routing_key : key of route
        login : user login
        password : user password
        0,000
        """

        try:

            parameters = pika.URLParameters(
                'amqp://' + self.rbq_user_new + ':' + self.rbq_password_new + '@' + self.rbq_host_new + ':' + self.rbq_port_new + '/%2F')

            _logger.info("\nBegin run publish")
            _logger.info("\n\nGet parameters :")
            _logger.info(parameters)

            if not trigram:
                trigram = self.rbq_trigram_new
            if not delivery:
                delivery = self.get_attribute_data("name")
            if not origin:
                origin = self.get_attribute_data("origin")
            if eshop_id == "":
                eshop_id = self.get_instance_ecommerce()[0]
            if eshop_url == "":
                eshop_url = self.get_instance_ecommerce()[1]

            headers = {
                "subject-id": self.get_attribute_data("name") or '',
                "context": self.rbq_trigram_new,
                "source": "Odoo",
                "odoo": "V16",
                "domain": "delivery",
                "event-name": self.get_attribute_data("rbq_event_status_new", "") or '',
                "new-state": self.get_attribute_data("rbq_new_status_new", "") or '',
                "timestamp_in_ms": dt.fromtimestamp(datetime.datetime.now().timestamp())
                
            }
            if not message:
                message = {
                    "origin-id": origin,
                    "eshop-url": eshop_url,
                    "eshop-id": eshop_id,
                    "carrier-id": self.get_attribute_data("carrier_id", "id") or '',
                    "carrier-name": self.get_attribute_data("carrier_id", "name") or '',
                    "carrier-cle-log-1": self.get_attribute_data("carrier_id", "name_l4") or '',
                    "carrier-cle-log-2": self.get_attribute_data("carrier_id", "name_l4_key2") or '',
                    "scheduled-date": self.get_attribute_data("scheduled_date") or '',
                    "global-channel": self.get_attribute_data("global_channel_id", "name") or '',
                    "picking-type": self.get_attribute_data("picking_type_id", "name") or '',
                    "weight": self.get_attribute_data("weight") or 0,
                    "shipping-weight": self.get_attribute_data("shipping_weight") or '',
                    "Id_Group": self.get_attribute_data("idgroup") or '',
                    "Id_Canal": self.get_attribute_data("idcanal") or '',
                    "Type-CDE": self.get_attribute_data("typecmd") or '',
                    "partner-name": self.get_attribute_data("partner_id", "name") or '',
                    "partner-street": self.get_attribute_data("partner_id", "street") or '',
                    "partner-street2": self.get_attribute_data("partner_id", "street2") or '',
                    "partner-zip": self.get_attribute_data("partner_id", "zip") or '',
                    "partner-city": self.get_attribute_data("partner_id", "city") or '',
                    "partner-country": self.get_attribute_data("partner_id", "country_id") or '',
                    "partner-phone": self.get_attribute_data("partner_id", "phone") or '',
                    "partner-mobile": self.get_attribute_data("partner_id", "mobile") or '',
                    "partner-email": self.get_attribute_data("partner_id", "email") or '',
                    "move-type": self.get_attribute_data("move_type") or '',
                    "picking-line": self.get_picking_line_data(),
                    "status": self.get_attribute_data("state") or '',
                    "substate": self.get_attribute_data("textual_substate") or ''

                }

            message = str(json.dumps(message, default = str))

            _logger.info("Content - RabbitMQ Odoo V16 :")
            _logger.info(message)

            connection = pika.BlockingConnection(
                parameters)

            _logger.info("Connection value - RabbitMQ Odoo V16")
            _logger.info(connection)
            channel = connection.channel()
 

            _logger.info("Channel : RabbitMQ Odoo V16")
            _logger.info(channel)
 


            properties = pika.BasicProperties(
                content_type='application/json',
                headers=headers)

            res = channel.basic_publish(exchange=self.rbq_exchange_new, routing_key=routing_key, body=message,
                                        properties=properties)
            _logger.info("Result of publish : RabbitMQ Odoo V16")
            _logger.info(res)
            connection.close()
            _logger.info("\nEnd run publish")

        except Exception as er:
            _logger.error("############### ERROR begin ##############")
            _logger.error("\n\nError publish RabbitMQ: ", str(er), " - RabbitMQ Odoo V16")
            _logger.error("############### ERROR end ##############")