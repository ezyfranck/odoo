# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, models, fields, api
from odoo.addons.queue_job.job import job
# from odoo.addons.connector.components.mapper import (
#     mapping,
#     only_create,
# )
# from ...components.importer import (
#     import_record,
#     import_batch,
# )
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


import datetime
import logging
_logger = logging.getLogger(__name__)

try:
    import html2text
except ImportError:
    _logger.debug('Cannot import `html2text`')

try:
    from bs4 import BeautifulSoup
except ImportError:
    _logger.debug('Cannot import `bs4`')

try:
    from prestapyt import PrestaShopWebServiceError
except ImportError:
    _logger.debug('Cannot import from `prestapyt`')


class ProductTemplateMapper(Component):
    _inherit = 'prestashop.product.template.mapper'
    _apply_on = 'prestashop.product.template'


    def get_uom_and_ratio(self, record):
        
        return


    @mapping
    def apply_dimensions(self, record):
        #Prestashop dimensions are expressed in meters in the API
        width = record['width']
        height = record['height']
        depth = record['depth']
        dimensional_uom_id = False
        
        #Get the dimension for the existing product
        binder = self.binder_for('prestashop.product.template')
        template = binder.to_internal(record['id'], unwrap=True)
        if template and template.dimensional_uom_id.id :
            dimensional_uom_id = template.dimensional_uom_id
        else:
            dimensional_uom_id = self.env['product.uom'].search([
                ('category_id', '=', self.env.ref('product.uom_categ_length').id),
                ('uom_type', '=', 'reference')
                ])
        
        factor_inv = dimensional_uom_id.factor_inv
        width = float(width) / factor_inv
        height = float(height) / factor_inv
        depth = float(depth) / factor_inv

        return { 'width' : width,
                 'height': height,
                 'length': depth,
                 'dimensional_uom_id' : dimensional_uom_id.id
                 }
        
            
