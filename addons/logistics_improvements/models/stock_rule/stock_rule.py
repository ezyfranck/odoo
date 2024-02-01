# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models
from odoo.osv import expression


class StockRule(models.Model):
    _inherit = "stock.rule"


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    # @Emmanuel
    def _get_moves_to_assign_domain(self, company_id):
        domain = super(ProcurementGroup, self)._get_moves_to_assign_domain(company_id)
        exclude_moves = self.env["stock.move"]._moves_to_exclude_from_mrp()
        # TODO: Fix bad usage of AND expression
        domain = expression.AND([domain, [("id", "not in", exclude_moves.ids)]])
        return domain
