# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime as datetime_package
import logging
from datetime import datetime, timedelta

from odoo import fields, models
from odoo.addons import decimal_precision as dp
from odoo.fields import first
from odoo.tools import parse_date

_logger = logging.getLogger(__name__)


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    team_id = fields.Many2one(
        'crm.team', string='Sales Team',
        default=lambda self: self.env["crm.team"]
        .sudo()
        ._get_default_team_id(user_id=self.env.uid))
    
    
class Picking(models.Model):
    _inherit = "stock.picking"

    team_id = fields.Many2one(
        'crm.team', string='Sales Team',
        default=lambda self: self.env["crm.team"]
        .sudo()
        ._get_default_team_id(user_id=self.env.uid))
    
class Move(models.Model):
    _inherit = "stock.move"

    team_id = fields.Many2one(
        'crm.team', string='Sales Team',
        default=lambda self: self.env["crm.team"]
        .sudo()
        ._get_default_team_id(user_id=self.env.uid))
    
    def _get_new_picking_values(self):
        values=super(Move, self)._get_new_picking_values()
        values.update({
                'team_id': self.mapped('team_id').id
            })
        return values
    
class Rule(models.Model):
    _inherit = "stock.rule"

    # def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
    #     move_values = super(Rule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
    #     team_id = values.get('team_id')
    #     move_values.update({
    #             'team_id': team_id.id or False
    #         })
    #     return move_values
    def _get_custom_move_fields(self):
        """The purpose of this method is to be override in order to easily add
        fields from procurement 'values' argument to move data.
        """
        ret = super(Rule, self)._get_custom_move_fields()
        ret.append("team_id")
        return ret
    