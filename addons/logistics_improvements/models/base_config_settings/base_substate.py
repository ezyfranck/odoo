import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class BaseSubstateType(models.Model):
    _inherit = "base.substate.type"

    model = fields.Selection(
        selection_add=[
            ("stock.picking", "Stock Picking"),
            ("stock.move", "Stock Moves"),
        ],
        ondelete={"stock.picking": "cascade", "stock.move": "cascade"},
    )


class BaseSubstate(models.Model):
    _inherit = "base.substate"

    is_logistics_state = fields.Boolean(string="Is logistic state to protect")
    exclude_state_from_mrp = fields.Boolean(
        string="Exclude states from mrp reservation"
    )

    display_in_status_bar = fields.Boolean(string="Display in status Bar")
