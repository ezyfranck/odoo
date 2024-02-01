import functools
import logging

from lxml import etree
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


IDCANAL = [
    ("WEB", "WEB"),
    ("PRO", "PRO"),
    ("MARKETPLACE", "MARKETPLACE"),
    ("DISTRIBUTEUR", "DISTRIBUTEUR"),
    ("REASSORT", "REASSORT"),
    ("SPECIAL", "SPECIAL"),
]


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "base.substate.mixin"]

    @api.depends("move_ids")
    def calc_summary_fields(self):
        for pick in self:
            pick.product_qty = 0
            pick.lines_qty = len(pick.move_ids)
            if pick.lines_qty == 0:
                return
            lines = pick.move_ids.filtered(lambda r: r.product_id.type == "product")
            pick.ref_qty = len(lines)
            if len(lines) > 0:
                pick.product_qty = functools.reduce(
                    lambda x, y: x + y, [z.product_uom_qty for z in lines]
                )

    def compute_need_backorder(self):
        # TODO: more explict variable names and purpose
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

    # TODO: Challenge EZY for use of this
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

    def _check_backorder(self):
        # If strategy == 'manual', let the normal process going on
        self = self.filtered(lambda p: p.backorder_strategy == "ask")
        return super(StockPicking, self)._check_backorder()

    def _create_backorder(self):
        # Do nothing with pickings 'no_create'
        pickings = self.filtered(lambda p: p.backorder_strategy != "never")
        pickings_no_create = self - pickings
        # TODO : check below, looks like the cancelation is not propagated
        # TODO: Also, things seems to stay reserved
        pickings_no_create.mapped("move_ids")._cancel_remaining_quantities()

        res = super(
            StockPicking, pickings.with_context(bypass_assign_for_backorder=True)
        )._create_backorder()
        to_cancel = res.filtered(
            lambda b: b.backorder_id.backorder_strategy == "cancel"
        )
        to_cancel.action_cancel()
        return res

    backorder_strategy = fields.Selection(
        [
            ("ask", "Manual"),#ask
            ("always", "Create"),#always
            ("never", "No create"),#never
            ("cancel", "Cancel"),
        ],
        default="ask",
        help="Define what to do with backorder",
        required=True,
    )

    def _check_logistics_acl_for_validate(self):
        has_acl = self.env.user.has_group(
            "logistics_improvements.can_change_logistics_states"
        )
        return has_acl

    def _ckeck_logistics_states_security(self):
        logistics_pickings = self._logistics_pickings()
        concerned_pickings = self & logistics_pickings
        if (
            len(concerned_pickings) > 0
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
    def _logistics_pickings(self, additionnal_domain=[]):
        """Use this method to get the picking in a logistic state
        that should be excluded from reservation
        usefull for assign, unreserve etc...
        """
        substate_domain = self._get_default_substate_domain(state_val="assigned")
        # logistics_domain = substate_domain
        # TODO :  FIX expression
        logistics_domain = expression.AND(
            [[("is_logistics_state", "=", True)], additionnal_domain]
        )
        logistics_domain = expression.AND([substate_domain, logistics_domain])
        logistics_substate_ids = self.env["base.substate"].search(logistics_domain)

        logistics_pickings = self.search(
            [
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
        return logistics_pickings

    @api.model
    def _picking_to_exclude_from_mrp(self):
        """Use this method to get the picking in a logistic state
        that should be excluded from reservation
        usefull for assign, unreserve etc...
        """
        picking_to_exclude_ids = self._logistics_pickings(
            additionnal_domain=[
                ("exclude_state_from_mrp", "=", True),
            ]
        )
        return picking_to_exclude_ids

    show_unreserve = fields.Boolean(
        compute="_compute_show_validate",
        help='Technical field used to decide whether the button "Unreserve" should be displayed.',
    )

    @api.depends("substate_id", "textual_substate")
    def _compute_show_validate(self):
        super()._compute_show_validate()
        for picking in self:
            show_validate = picking.show_validate
            # Reimplement by code this conditions : https://github.com/OCA/OCB/blob/14.0/addons/stock/views/stock_picking_views.xml#L253
            hide_unreserve = (
                picking.picking_type_code == "incoming"
                or picking.immediate_transfer == True
            ) or (
                (
                    picking.state not in ("assigned", "partially_available")
                    and picking.move_type != "one"
                )
                or (
                    picking.state
                    not in ("assigned", "partially_available", "confirmed")
                    and picking.move_type == "one"
                )
            )
            show_unreserve = not hide_unreserve or False
            if (
                picking.textual_substate
                and picking.textual_substate != "ready_for_logistics"
            ):
                show_validate = False
                show_unreserve = False

            if picking.textual_substate and picking._check_logistics_acl_for_validate():
                show_validate = True
                show_unreserve = True

            picking.show_validate = show_validate
            picking.show_unreserve = show_unreserve

    @api.depends(
        "move_type",
        "move_ids.textual_substate",
        "move_ids.substate_id",
    )
    def _compute_state(self):
        super()._compute_state()
        self._compute_substate()

    @api.depends(
        "move_type",
        "move_ids.state",
        "move_ids.picking_id",
        "move_ids.substate_id",
        "move_ids.textual_substate",
    )
    def _compute_substate(self):
        self.mapped("move_ids_without_package")  # prefetch
        for pick in self:
            substates = pick.move_ids_without_package.mapped("textual_substate")
            substates = [sb for sb in substates if sb != ""]
            # target_substate_id = self._get_default_substate_id(state_val=pick.state)

            if len(substates) == 0:
                target_substate_id = self.env["base.substate"]
            else:
                if "refused_by_logistics" in substates:
                    target_substate_id = pick._get_substate_by_text(
                        state_val=pick.state, substate_name="refused_by_logistics"
                    )
                elif "cancelled_by_logistics" in substates:
                    target_substate_id = pick._get_substate_by_text(
                        state_val=pick.state, substate_name="cancelled_by_logistics"
                    )
                else:
                    target_substate_id = pick._get_substate_by_text(
                        state_val=pick.state, substate_name=substates[:1]
                    )

            pick.substate_id = target_substate_id
            pick.textual_substate = target_substate_id.name or ""
            pick.textual_substate_done = pick.textual_substate

    def _get_substate_by_text(self, state_val=False, substate_name=False):
        """Override this method
        to change domain values
        """
        domain = self._get_default_substate_domain(state_val=state_val)
        if not isinstance(substate_name, list):
            substate_name = [substate_name]
        domain += [("name", "in", substate_name)]
        substate_id = self.env["base.substate"].search(domain, limit=1)
        return substate_id

    def _get_substate_to_display(self, state_val=False):
        substate_domain = self._get_default_substate_domain(state_val=state_val)
        statusbar_substate_ids = self.env["base.substate"].search(substate_domain)
        visible_status_ids = statusbar_substate_ids.filtered(
            lambda s: s.display_in_status_bar == True
        )
        visible_status = ",".join([str(item.name) for item in visible_status_ids])
        return visible_status

    def _get_substate_selection(self):
        assigned_substate_domain = self._get_default_substate_domain(
            state_val="assigned"
        )
        done_substate_domain = self._get_default_substate_domain(state_val="done")
        status_bar_domain = expression.OR(
            [assigned_substate_domain, done_substate_domain]
        )
        statusbar_substate_ids = self.env["base.substate"].search(status_bar_domain)
        selection = [(l.name, l.name) for l in statusbar_substate_ids]
        return selection

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        result = super(StockPicking, self).fields_view_get(
            view_id, view_type, toolbar, submenu
        )
        if view_type == "form":
            doc = etree.XML(result["arch"])
            node_assigned = doc.xpath(
                "//header[@name='substate']//field[@name='textual_substate']"
            )
            if node_assigned:
                assigned_statusbar_visible = self._get_substate_to_display(
                    state_val="assigned"
                )
                node_assigned[0].set("statusbar_visible", assigned_statusbar_visible)

            node_done = doc.xpath(
                "//header[@name='substate']//field[@name='textual_substate_done']"
            )
            if node_done:
                done_statusbar_visible = self._get_substate_to_display(state_val="done")
                node_done[0].set("statusbar_visible", done_statusbar_visible)
            result["arch"] = etree.tostring(doc)
        return result

    textual_substate = fields.Selection(
        selection=_get_substate_selection,
        string="Textual value of the substate",
        compute_sudo=_compute_substate,
        store=True,
        copy=False,
    )

    # TODO: As I didn't succeed in makig 2 statusbar on the same field in XML
    # I decided to split the field regarding the stats whihc is really a bad way to do.
    textual_substate_done = fields.Selection(
        selection=_get_substate_selection,
        string="Textual value of the substate in case of done",
        compute_sudo=_compute_substate,
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
            "backorder_strategy": picking_type_id.create_backorder,
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
                picking.backorder_strategy = picking_type_id.create_backorder

    @api.onchange("partner_id")
    @api.depends("partner_id")
    def onchange_logistics_info(self):
        self.idcanal = self.partner_id.idcanal
        self.typecmd = self.partner_id.typecmd
        self.idgroup = self.partner_id.idgroup

    def button_validate_logistic(self):
        # defensive method to be called via API to be sure that xmlrpc retrun something
        self.ensure_one()
        self.button_validate()
        return True

    def button_reset_refused_by_logistic(self):
        for rec in self:
            rec.write_log_states("ready_for_logistics")

    # TODO: check this defensive to prevent unappropriates updates
    def write_log_states(self, state):
        for pick in self:
            # if pick.state in ["draft", "cancel", "waiting", "confirmed", "done"]:
            #     raise ValidationError(
            #         _(
            #             "[LOG]Setting logistic states on %s with state %s is not allowed!"
            #         )
            #         % (pick.name, pick.state)
            #     )
            # #TODO: check states
            # if state not in ["l4_sent", "l4_refused", "l4_preparation"]:
            #     raise ValidationError(
            #         _("[LOG]Setting non logistic states %s on %s is not allowed!")
            #         % (state, pick.name)
            #     )
            pick.move_ids.write({"textual_substate": state})

        return True

    def _update_before_write_create(self, values):
        self._ckeck_logistics_states_security()
        return super()._update_before_write_create(values)

    def action_assign(self):
        """In addition to what the method in the parent class does,
        Changed batches states to assigned if all picking are assigned.
        """
        bypass_assign_for_backorder = self.env.context.get(
            "bypass_assign_for_backorder", False
        )
        native_pick_ids = self - self._picking_to_exclude_from_mrp()
        if bypass_assign_for_backorder:
            native_pick_ids = self
        _logger.info(
            "Don't assign for the following pickings %s because of the logistics states"
            % (self - native_pick_ids)
        )
        return super(StockPicking, native_pick_ids).action_assign()

    def do_unreserve(self):
        native_pick_ids = self - self._picking_to_exclude_from_mrp()
        bypass_logistics_states = self.env.context.get("bypass_logistics_states", False)
        if bypass_logistics_states:
            _logger.info(
                "Unreserved called in a context where we want to ignore the reservation exclusion"
            )
            native_pick_ids = self

        super(StockPicking, native_pick_ids).do_unreserve()


    