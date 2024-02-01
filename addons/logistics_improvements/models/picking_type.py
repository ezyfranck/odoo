import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class L4StockPickingType(models.Model):
    _name = "l4.stock.picking.type"
    _description = "Logistics typology for Picking type"

    move_code = fields.Char(string="Mouvement Code for L4", required=True)
    move_reason = fields.Char(
        string="Reason of the move for L4",
        required=True,
    )
    direction = fields.Char(string="Direction of the operation")

    _sql_constraints = [
        (
            "logistiq_code_reason_direction_uniq",
            "unique(move_reason, move_code, direction)",
            """A logistics type with the same move_reason,
            move_code and direction already exists.""",
        ),
    ]


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    l4_types = fields.Many2many(comodel_name="l4.stock.picking.type")

    default_blocked_for_logistics = fields.Boolean(
        string="blocked for logistics",
        default=False,
        help="""
        This option has no specific action in Odoo.\n
        It's used to inform logistics that pickings of this type
        will be 'by default'  available to be send to logistics.
        """,
    )
    default_managed_by_date = fields.Boolean(
        string="Managed by date",
        default=False,
        help="""
        This option has no specific action in Odoo.\n
        It's used to inform logistics that pickings of this type
        will be 'by default' based on the scheduled_date
        as a criteria for exporting to logistics.
        """,
    )
