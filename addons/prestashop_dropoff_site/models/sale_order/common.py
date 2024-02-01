# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import timedelta
from prestapyt import PrestaShopWebServiceDict
from odoo import api, fields, models
from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    mr_relay_number = fields.Char("Mondial Relay ID", store=True)

    def select_relay_with_mr(self):
        if self.mr_relay_number :
            if not self.carrier_id.id and not self.carrier_id.with_dropoff_site :
                raise ValidationError(_("Carrier self.carrier_id.id %s hasn't dropoffsite configure but this order %s has a relay code %s") % (self.carrier_id.id,self.name,self.mr_relay_number))
            else :
                site_ids=self.env['dropoff.site'].search([('code','=',self.mr_relay_number),('carrier_id','=', self.carrier_id.id)])
                site_id = site_ids[:1]
                if len(site_ids) > 0:
                    
                    if not site_id.partner_id.id :
                        partner_id = self.env['res.partner'].create({'name': ("%s %s" % (self.carrier_id.name,self.mr_relay_number)) })
                        site_id.partner_id=partner_id
                else :
                    partner_id = self.env['res.partner'].create({'name': ("%s %s" % (self.carrier_id.name,self.mr_relay_number)) })
                    site_id = self.env['dropoff.site'].create({'code' : self.mr_relay_number,
                                                     'carrier_id' : self.carrier_id.id,
                                                     'partner_id': partner_id.id})
                    site_id.partner_id=partner_id
                self.final_shipping_partner_id = self.partner_shipping_id
                self.partner_shipping_id=site_id.partner_id
            
    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        res.select_relay_with_mr()
        return res
        
                        