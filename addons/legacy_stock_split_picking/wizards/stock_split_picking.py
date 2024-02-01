# Copyright 2020 Hunki Enterprises BV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockSplitPicking(models.TransientModel):
    _inherit = "stock.split.picking"
    _description = "Split a picking"

    @api.onchange("mode")
    def onchange_mode(self):
        self.move_ids = self.picking_ids.mapped("move_lines")

    mode = fields.Selection(
        selection_add=[
            ("done_v10", "Explicit values (v10)"),
        ],
        ondelete={
            "done_v10": "set default",
        },
    )

    move_line_ids = fields.Many2many(
        comodel_name="stock.move.line",
        string="Split Operations",
        default=lambda self: self._default_move_line_ids(),
    )

    def _default_move_line_ids(self):
        picking_id = self.env["stock.picking"].browse(
            self.env.context.get("active_ids", [])
        )
        return picking_id.move_line_ids

    # def _apply_done_v10(self):
    #     move_with_full_done_qty = self.move_line_ids.filtered(
    #         lambda m: m.qty_done != 0.0 and m.qty_done == m.product_qty
    #     )
    #     move_with_no_done_qty = self.move_line_ids.filtered(lambda m: m.qty_done == 0.0)
    #     move_with_partial_qty_done = self.move_line_ids.filtered(
    #         lambda m: m.qty_done != 0.0 and m.qty_done != m.product_uom_qty
    #     )

    #     is_same_moves = self.mapped("picking_ids").move_line_ids == self.move_line_ids

    #     if (
    #         len(move_with_full_done_qty)
    #         and len(move_with_no_done_qty)
    #         and len(move_with_partial_qty_done)
    #     ):
    #         raise UserError(
    #             _(
    #                 "You can't mix strategy for splittig\n"
    #                 "Either choose partial quantity done or full quantity"
    #             )
    #         )

    #     return self.mapped("picking_ids").split_process()

    def _apply_done_v10(self):
        return self.mapped("picking_ids").split_process()
