# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import logging

from odoo import models

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def name_get(self):
        result = super(ResPartner, self).name_get()
        for result_iterate in result:
            partner_id = self.env["res.partner"].browse(result_iterate[0])
            if partner_id.type == 'delivery':
                reserch_name= partner_id._get_contact_name(partner_id, partner_id.name)
                name = result_iterate[1].replace(reserch_name, partner_id.name)
                if  not self.env.context.get("show_address", False):
                    old_name = partner_id.name or ''
                    zip = partner_id.zip  or ''
                    street = partner_id.street or ''
                    city = partner_id.city or ''
                    country = partner_id.country_id.name or ''
                    delivery =  '[LIV][%s - %s %s %s]' % (zip, street, city, country)
                    name = '%s %s' % (old_name, delivery)
                new_tuple = []
                new_tuple = (partner_id.id, name)
                index_tuple = result.index(result_iterate)
                result[index_tuple] = new_tuple
        return result
