# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


import logging

from odoo import models

_logger = logging.getLogger(__name__)


class PrestashopSaleOrder(models.Model):
    _inherit = "prestashop.sale.order"

    # TODO: match on id_default_group to allow
    def _update_workflow_from_partner_category(self):
        bind_partner_id = self.commercial_partner_id.prestashop_bind_ids
        ps_category_id = bind_partner_id.default_category_id

        workflow_id = self.env["sale.workflow.process"].search(
            [
                ("prestashop_partner_category", "in", [ps_category_id.id]),
            ],
            limit=1,
        )
        _logger.debug(
            "PS: Found workflow %s for %s matching category %s"
            % (workflow_id, bind_partner_id, ps_category_id)
        )
        if len(workflow_id):
            order_id = self.odoo_id
            self.write({"workflow_process_id": workflow_id.id})
            order_id._onchange_workflow_process_id()
            _logger.debug(
                "PS: Workflow %s updated for order %s" % (workflow_id, order_id.name)
            )


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # @api.onchange("payment_mode_id")
    # def onchange_payment_mode_set_workflow(self):
    #     if self.payment_mode_id.workflow_process_id:
    #         self.workflow_process_id = self.payment_mode_id.workflow_process_id
