import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move", "base.substate.mixin"]

    l4_xml_file = fields.Char(string="Fichier logistique")
    l4_line_id = fields.Integer(string="Id ligne fichier logistique")

    def _cancel_remaining_quantities(self):
        to_cancel = self.filtered(lambda m: m.state not in ("done", "cancel"))
        to_cancel._action_cancel()

    def _ckeck_logistics_states_security(self):
        logistics_moves = self._logistics_moves()
        concerned_moves = self & logistics_moves
        if (
            len(concerned_moves) > 0
            and not self.env.user.has_group(
                "logistics_improvements.can_change_logistics_states"
            )
            and self.env.user.id != 1
        ):
            raise UserError(
                _(
                    "Changing stock move in logistics states is not possible.\nPlease contact your EZYLOG administrator"
                )
            )

    @api.model
    def _logistics_moves(self, additionnal_domain=[]):
        """Get all the logistics stock.move with substate marked as logistics
        very convenient to use
        """
        substate_domain = self._get_default_substate_domain(state_val="assigned")
        # logistics_domain = substate_domain
        # TODO don't mix domains
        logistics_domain = expression.AND(
            [[("is_logistics_state", "=", True)], additionnal_domain]
        )
        logistics_domain = expression.AND([substate_domain, logistics_domain])
        logistics_substate_ids = self.env["base.substate"].search(logistics_domain)
        logistics_pickings = self.env["stock.picking"]._logistics_pickings(
            additionnal_domain=additionnal_domain
        )

        logistics_moves = self.search(
            [
                "|",
                ("picking_id", "in", logistics_pickings.ids),
                "&",
                ("substate_id", "in", logistics_substate_ids.ids),
                (
                    "state",
                    "in",
                    logistics_substate_ids.mapped("target_state_value_id").mapped(
                        "target_state_value"
                    ),
                ),
            ]
        )
        return logistics_moves

    @api.model
    def _moves_to_exclude_from_mrp(self):
        """Use this method to get the picking in a logistic state
        that should be excluded from reservation
        usefull for assign, unreserve etc...
        """
        move_to_exclude_ids = self._logistics_moves(
            additionnal_domain=[
                ("exclude_state_from_mrp", "=", True),
            ]
        )
        return move_to_exclude_ids

    def _get_substate_by_text(self, state_val=False, substate_name=False):
        """Override this method
        to change domain values
        """
        domain = self._get_default_substate_domain(state_val=state_val)
        domain += [("name", "=", substate_name)]
        substate_id = self.env["base.substate"].search(domain, limit=1)
        return substate_id

    @api.depends("state", "substate_id")
    def _compute_textual_state(self):
        self.mapped("substate_id") #prefetch
        for move in self:
            move.textual_substate = move.substate_id.name or ""

    def _write_logistic_substate(self):
        for mv in self:
            if not mv.textual_substate:
                continue
            substate_id = self._get_substate_by_text(
                state_val=mv.state, substate_name=mv.textual_substate
            )

            mv.write(
                {
                    "substate_id": substate_id.id,
                    # 'textual_substate': substate_id.name or ""
                }
            )
            if not substate_id.id:
                mv.textual_substate = ""

    # TODO : implement the inverse method to ease EZY stuff
    textual_substate = fields.Char(
        string="Textual value of the substate",
        compute=_compute_textual_state,
        inverse=_write_logistic_substate,
        store=True,
        copy=False,
    )

    def _get_default_substate_id(self, state_val=False):
        """Gives default substate_id"""
        search_domain = self._get_default_substate_domain(state_val)
        # perform search, return the first found
        return (
            self.env["base.substate"]
            .search(search_domain, order="sequence", limit=1)
            .id
        )

    def _get_default_substate_domain(self, state_val=False):
        """Override this method
        to change domain values
        """
        domain = super()._get_default_substate_domain(state_val=state_val)
        if (
            len(self)
            and "incoming" not in self.mapped("picking_code")
            and "outgoing" not in self.mapped("picking_code")
        ):
            domain += [("name", "=", "not_concerned")]

        return domain


    def _update_before_write_create(self, values):
        self._ckeck_logistics_states_security()
        return super()._update_before_write_create(values)

    # MRP RESEVATION PART
    def _search_picking_for_assignation(self):
        self.ensure_one()
        # exclude picking in logistic state
        # Need to override all method because the search as limit = 1
        # exclude_pick = self.env["stock.picking"]._logistics_pickings()
        exclude_pick = self.env["stock.picking"]._picking_to_exclude_from_mrp()
        domain = [
            ("group_id", "=", self.group_id.id),
            ("location_id", "=", self.location_id.id),
            ("location_dest_id", "=", self.location_dest_id.id),
            ("picking_type_id", "=", self.picking_type_id.id),
            ("printed", "=", False),
            ("immediate_transfer", "=", False),
            (
                "state",
                "in",
                ["draft", "confirmed", "waiting", "partially_available", "assigned"],
            ),
            ("id", "not in", exclude_pick.ids),
        ]
        if self.partner_id and (
            self.location_id.usage == "transit"
            or self.location_dest_id.usage == "transit"
        ):
            domain += [("partner_id", "=", self.partner_id.id)]
        picking = self.env["stock.picking"].search(domain, limit=1)
        return picking

    def _do_unreserve(self):
        native_moves = self - self._moves_to_exclude_from_mrp()
        return super(StockMove, native_moves)._do_unreserve()

    def _action_assign(self, force_qty=False):
        native_moves = self - self._moves_to_exclude_from_mrp()
        return super(StockMove, native_moves)._action_assign(force_qty)

    def _trigger_assign(self):
        native_moves = self - self._moves_to_exclude_from_mrp()
        return super(StockMove, native_moves)._trigger_assign()

    def _should_bypass_reservation(self,forced_location=False):
        """This one seems to be the ultimate"""
        self.ensure_one()
        if self in self._moves_to_exclude_from_mrp():
            return True
        return super(StockMove, self)._should_bypass_reservation(forced_location)
    
    def _assign_picking(self):
        result = super(StockMove, self)._assign_picking()
        vals = {}
        for move in self:
            if move.picking_id.sale_id:
                vals.update(
                    {
                        "idcanal": move.picking_id.sale_id.idcanal,
                        "idgroup": move.picking_id.sale_id.idgroup,
                        "typecmd": move.picking_id.sale_id.typecmd,
                    }
                )
                move.picking_id.write(vals)

        return result
