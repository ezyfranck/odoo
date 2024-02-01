import functools
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare

from .stock_move import LOGISTICS_MOVE_STATE_LIST

_logger = logging.getLogger(__name__)


LOGISTICS_PICK_STATE = [
    ("l4_sent", _("Sent to Logistics")),
    ("l4_refused", _("Refused by logistics")),
    ("l4_preparation", _("Preparation")),
]

IDCANAL = [
    ("WEB", "WEB"),
    ("PRO", "PRO"),
    ("MARKETPLACE", "MARKETPLACE"),
    ("DISTRIBUTEUR", "DISTRIBUTEUR"),
    ("REASSORT", "REASSORT"),
    ("SPECIAL", "SPECIAL"),
]


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def change_order_state(self):
        #        _logger.debug("CHANGE ORDER STATE %s" % self)
        for pick in self:
            # TODO : change the criteria for taking account of L23 of salestock
            if pick.sale_id and pick.state:
                sale_id = self.env["sale.order"].browse(pick.sale_id.id)
                if pick.state == "l4_preparation" and sale_id.state != "l4_preparation":
                    sale_id.write({"state": "l4_preparation"})
                sale_id.get_delivered_state()

    @api.depends("move_type", "move_lines.state", "move_lines.picking_id")
    def _compute_state(self):
        """State of a picking depends on the state of its related stock.move
        - Draft: only used for "planned pickings"
        - Waiting: if the picking is not ready to be sent so if
          - (a) no quantity could be reserved at all or if
          - (b) some quantities could be reserved and the shipping policy is
          "deliver all at once"
        - Waiting another move: if the picking is waiting for another move
        - Ready: if the picking is ready to be sent so if:
          - (a) all quantities are reserved or if
          - (b) some quantities could be reserved and the shipping policy
          is "as soon as possible"
        - Done: if the picking is done.
        - Cancelled: if the picking is cancelled
        """
        for picking in self:
            if not picking.move_lines:
                picking.onchange_logistics_info()
                picking.state = "draft"
            elif any(
                move.state == "draft" for move in picking.move_lines
            ):  # TDE FIXME: should be all ?
                picking.state = "draft"
            elif all(move.state == "cancel" for move in picking.move_lines):
                picking.state = "cancel"
            elif all(move.state in ["cancel", "done"] for move in picking.move_lines):
                picking.state = "done"

            elif any([x.state == "l4_sent" for x in picking.move_lines]):
                picking.state = "l4_sent"
            elif any([x.state == "l4_refused" for x in picking.move_lines]):
                picking.state = "l4_refused"
            elif any(
                [x.state == "l4_preparation" for x in picking.move_lines],
            ):
                picking.state = "l4_preparation"
            else:
                relevant_move_state = (
                    picking.move_lines._get_relevant_state_among_moves()
                )
                if relevant_move_state == "partially_available":
                    picking.state = "assigned"
                else:
                    picking.state = relevant_move_state

    @api.depends("move_lines")
    def calc_summary_fields(self):
        for pick in self:
            pick.product_qty = 0
            pick.lines_qty = len(pick.move_lines)
            if pick.lines_qty == 0:
                return
            lines = pick.move_lines.filtered(lambda r: r.product_id.type == "product")
            pick.ref_qty = len(lines)
            if len(lines) > 0:
                pick.product_qty = functools.reduce(
                    lambda x, y: x + y, [z.product_uom_qty for z in lines]
                )

    def compute_need_backorder(self):
        for pick in self:
            test = pick._check_backorder()
            if not test:
                pick.need_backorder = False
            else:
                pick.need_backorder = True

    need_backorder = fields.Boolean(
        string="need backorder", compute=compute_need_backorder
    )

    idcanal = fields.Selection(
        selection=IDCANAL,
        string="IDCANAL (Logistics)",
        index=True,
        tracking=True,
    )
    typecmd = fields.Char(
        string="Type Commande (Logistics)",
        tracking=True,
    )
    idgroup = fields.Char(string="IDGROUP (Logistics)")

    l4_id = fields.Char(string="Identifiant Logistique")
    wt_file = fields.Char(string="Fichier Welcome Track")
    wt_expe_log_file = fields.Char(string="Fichier Expedition Welcome Track")

    ref_qty = fields.Integer(
        string="Ref Qty",
        compute=calc_summary_fields,
    )
    product_qty = fields.Integer(
        string="Products qty",
        compute=calc_summary_fields,
    )
    lines_qty = fields.Integer(
        string="Line Number",
        compute=calc_summary_fields,
    )

    code_shipping_point = fields.Char("Code Shipping Point")
    code_relai = fields.Char(string="Relay Code")

    is_blocked_for_logistics = fields.Boolean(
        string="Blocked for logistics",
        # default=False,
        copy=False,
        tracking=True,
        help="""
        This option has no specific action in Odoo.\n
        It's used to inform logistics that this picking
        could be send to logistics.
        """,
    )
    is_managed_by_date = fields.Boolean(
        string="Managed by date for logistics",
        # default=False,
        copy=False,
        tracking=True,
        help="""
        This option has no specific action in Odoo.\n
        It's used to inform logistics that the scheduled_date
        is a criteria for exporting to logistics.
        """,
    )

    state = fields.Selection(
        compute=_compute_state,
        type="selection",
        copy=False,
        store=True,
        selection_add=LOGISTICS_PICK_STATE,
        string="Status",
        readonly=True,
        index=True,
        tracking=True,
        help="""
* Draft: not confirmed yet and will not be scheduled until confirmed\n
* Waiting Another Operation: waiting for another move to proceed before
it becomes automatically available (e.g. in Make-To-Order flows)\n
* Waiting Availability: still waiting for the availability of products\n
* Partially Available: some products are available and reserved\n
* Ready to Transfer: products reserved, simply waiting for confirmation.\n
* Sent to L4 : The picking has been sent to L4, waiting for validation
from their EDI.\n
* Transferred: has been processed, can't be modified or cancelled anymore\n
* Cancelled: has been cancelled, can't be confirmed anymore""",
    )

    @api.model_create_multi
    def create(self, vals_list):
        new_val_list = []
        for values in vals_list:
            if values.get("picking_type_id", False):
                picking_type_id = self.env["stock.picking.type"].browse(
                    [values["picking_type_id"]]
                )
                values = self._logistics_infos_vals(picking_type_id, values)
            new_val_list.append(values)
        res = super(StockPicking, self).create(new_val_list)
        return res

    def write(self, values):
        res = super(StockPicking, self).write(values)
        if "picking_type_id" in values:
            self.onchange_picking_type_id()
        return res

    def _logistics_infos_vals(self, picking_type_id, vals):
        # TODO: migrate this method in partner to return a json to have better factoring
        vals_from_picking_type_id = {
            "is_blocked_for_logistics": picking_type_id.default_blocked_for_logistics,
            "is_managed_by_date": picking_type_id.default_managed_by_date,
        }
        vals_from_picking_type_id.update(vals)
        return vals_from_picking_type_id

    @api.onchange("picking_type_id")
    @api.depends("picking_type_id")
    def onchange_picking_type_id(self):
        for picking in self:
            if len(picking.picking_type_id):
                picking_type_id = picking.picking_type_id
                picking.is_blocked_for_logistics = (
                    picking_type_id.default_blocked_for_logistics
                )
                picking.is_managed_by_date = picking_type_id.default_managed_by_date

    @api.onchange("partner_id")
    @api.depends("partner_id")
    def onchange_logistics_info(self):
        self.idcanal = self.partner_id.idcanal
        self.typecmd = self.partner_id.typecmd
        self.idgroup = self.partner_id.idgroup

    def do_prepare_partial(self):
        # TODO: This one is a full copy of the core
        # Imporve the strategy by keeping the move states in a variable
        # and use a method to change the state before calling the super.
        # Would be better

        PackOperation = self.env["stock.pack.operation"]

        # get list of existing operations and delete them
        existing_packages = PackOperation.search(
            [("picking_id", "in", self.ids)]
        )  # TDE FIXME: o2m / m2o ?
        if existing_packages:
            existing_packages.unlink()
        for picking in self:
            forced_qties = {}
            picking_quants = self.env["stock.quant"]
            # Calculate packages, reserved quants, qtys of this picking's moves
            for move in picking.move_lines:
                if move.state not in (
                    "assigned",
                    "confirmed",
                    "waiting",
                    "l4_sent",
                    "l4_preparation",
                ):
                    continue
                move_quants = move.reserved_quant_ids
                picking_quants += move_quants
                forced_qty = 0.0
                if move.state in ["assigned", "l4_sent", "l4_preparation"]:
                    qty = move.product_uom._compute_quantity(
                        move.product_uom_qty,
                        move.product_id.uom_id,
                        round=False,
                    )
                    forced_qty = qty - sum([x.qty for x in move_quants])
                # if we used force_assign() on the move,
                # or if the move is incoming, forced_qty > 0
                if (
                    float_compare(
                        forced_qty,
                        0,
                        precision_rounding=move.product_id.uom_id.rounding,
                    )
                    > 0
                ):
                    if forced_qties.get(move.product_id):
                        forced_qties[move.product_id] += forced_qty
                    else:
                        forced_qties[move.product_id] = forced_qty
            for vals in picking._prepare_pack_ops(
                picking_quants,
                forced_qties,
            ):
                vals["fresh_record"] = False
                PackOperation |= PackOperation.create(vals)
        # recompute the remaining quantities all at once
        self.do_recompute_remaining_quantities()
        for pack in PackOperation:
            pack.ordered_qty = sum(
                pack.mapped("linked_move_operation_ids")
                .mapped("move_id")
                .filtered(lambda r: r.state != "cancel")
                .mapped("ordered_qty")
            )
        self.write({"recompute_pack_op": False})

        return True

    def button_validate(self):
        """Reset the picking state to core
        for those coming from L4
        @return: True
        """
        # TDE FIXME: remove decorator when migration the remaining
        # TDE FIXME: draft -> automatically done, if waiting ?? CLEAR ME
        logistics_moves = self.mapped("move_lines").filtered(
            lambda self: self.state in ["l4_preparation", "l4_sent"]
        )
        logistics_moves.with_context(
            no_connector_export=True, connector_no_export=True, recompute=False
        ).write({"state": "assigned"})
        res = super(
            StockPicking,
            self.with_context(
                no_connector_export=False,
                connector_no_export=False,
                recompute=True,
            ),
        ).button_validate()
        self.change_order_state()
        return res

    def do_transfer(self):
        # DEPRECATED ?
        """For states coming from logistics, reset to usual state
        so that the normal flow will be followed.
        Prevent huge massive refactor."""
        _logger.debug("Possible useless method in v12, has to be deleted")
        logistics_moves = self.mapped("move_lines").filtered(
            lambda self: self.state
            in [
                "l4_preparation",
            ]
        )
        logistics_moves.write({"state": "assigned"})

        res = super(StockPicking, self).do_transfer()
        self.change_order_state()
        return res

    def button_validate_logistic(self):
        # defensive method to be called via API
        self.ensure_one()
        self.button_validate()
        return True

    def action_assign(self):
        """In addition to what the method in the parent class does,
        Changed batches states to assigned if all picking are assigned.
        """
        native_pick_ids = self.filtered(
            lambda self: self.state not in LOGISTICS_MOVE_STATE_LIST
        )
        _logger.info(
            "Don't assign for the following pickings %s because of the logistics states"
            % (self - native_pick_ids)
        )
        result = super(StockPicking, native_pick_ids).action_assign()
        return result

    # TODO: check this defensive to prevent unappropriates updates
    # def write(self, values):
    #     if 'state' in values:
    #         self.write_log_states(values.get('state', False))
    #         values.pop('state')
    #     res = super(StockPicking, self).write(values)
    #     return res

    def write_log_states(self, state):
        for pick in self:
            if pick.state in ["draft", "cancel", "waiting", "confirmed", "done"]:
                raise ValidationError(
                    _(
                        "[LOG]Setting logistic states on %s with state %s is not allowed!"
                    )
                    % (pick.name, pick.state)
                )
            if state not in ["l4_sent", "l4_refused", "l4_preparation"]:
                raise ValidationError(
                    _("[LOG]Setting non logistic states %s on %s is not allowed!")
                    % (state, pick.name)
                )
            pick.move_lines.write({"state": state})
            pick.change_order_state()
            return True
