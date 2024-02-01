import logging

from odoo import _, api, fields, models
from odoo.tools import float_compare, float_is_zero

_logger = logging.getLogger(__name__)

SALE_STATE = [
    # ('draft', _('Quotation')),
    # ('sent', _('Quotation Sent')),
    # ('sale', _('Sale Order')),
    ("l4_preparation", _("Preparation")),
    ("l4_shipped", _("Expedie")),
    # ('done', _('Done')),
    # ('cancel', _('Cancelled')),
]

IDCANAL = [
    ("WEB", "WEB"),
    ("PRO", "PRO"),
    ("MARKETPLACE", "MARKETPLACE"),
    ("DISTRIBUTEUR", "DISTRIBUTEUR"),
    ("REASSORT", "REASSORT"),
    ("SPECIAL", "SPECIAL"),
]


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "state", "product_uom_qty", "qty_delivered", "qty_to_invoice", "qty_invoiced"
    )
    def _compute_invoice_status(self):
        """
        Compute the invoice status of a SO line. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also hte default value if the conditions of no other status is met.
        - to invoice: we refer to the quantity to invoice of the line. Refer to method
          `_get_to_invoice_qty()` for more information on how this quantity is calculated.
        - upselling: this is possible only for a product invoiced on ordered quantities for which
          we delivered more than expected. The could arise if, for example, a project took more
          time than expected but we decided not to invoice the extra cost to the client. This
          occurs onyl in state 'sale', so that when a SO is set to done, the upselling opportunity
          is removed from the list.
        - invoiced: the quantity invoiced is larger or equal to the quantity ordered.
        """
        _logger.debug("M&GO _compute_invoice_status")
        orders = self.env["sale.order"]
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for line in self:
            orders &= line.order_id
            if line.state not in ("sale", "done", "l4_preparation", "l4_shipped"):
                line.invoice_status = "no"
            elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                line.invoice_status = "to invoice"
            elif (
                line.state in ("sale", "l4_preparation", "l4_shipped")
                and line.product_id.invoice_policy == "order"
                and float_compare(
                    line.qty_delivered, line.product_uom_qty, precision_digits=precision
                )
                == 1
            ):
                line.invoice_status = "upselling"
            elif (
                float_compare(
                    line.qty_invoiced, line.product_uom_qty, precision_digits=precision
                )
                >= 0
            ):
                line.invoice_status = "invoiced"
            else:
                line.invoice_status = "no"

        _logger.debug("ORDERS %s" % orders)
        orders.get_delivered_state()

    @api.depends("qty_invoiced", "qty_delivered", "product_uom_qty", "order_id.state")
    def _get_to_invoice_qty(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        for line in self:

            if line.order_id.state in ["sale", "done", "l4_preparation", "l4_shipped"]:
                if line.product_id.invoice_policy == "order":
                    line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        partner_shipping_id = self.env["res.partner"]
        if "partner_shipping_id" in vals and vals["partner_shipping_id"]:
            partner_shipping_id = self.env["res.partner"].browse(
                [vals["partner_shipping_id"]]
            )
        vals = self._logistics_infos_vals(partner_shipping_id, vals)
        res = super(SaleOrder, self).create(vals)
        return res

    def _logistics_infos_vals(self, partner_shipping_id, vals):
        # TODO: migrate this method in partner to return a json to have better factoring
        vals_from_partner = {
            "idcanal": partner_shipping_id.idcanal,
            "typecmd": partner_shipping_id.typecmd,
            "idgroup": partner_shipping_id.idgroup,
        }
        vals_from_partner.update(vals)
        return vals_from_partner

    @api.onchange("partner_shipping_id")
    @api.depends("partner_shipping_id")
    def onchange_logistics_info(self):
        vals = self._logistics_infos_vals(self.partner_shipping_id, {})
        self.idcanal = vals["idcanal"]
        self.typecmd = vals["typecmd"]
        self.idgroup = vals["idgroup"]

    fully_delivered = fields.Boolean("Fully Delivered", copy=False, default=False)
    state = fields.Selection(
        selection_add=SALE_STATE,
        string="Status",
        readonly=True,
        copy=False,
        index=True,
        tracking=True,
        default="draft",
    )

    idcanal = fields.Selection(
        selection=IDCANAL, string="IDCANAL (Logistics)", index=True
    )
    typecmd = fields.Char(string="Type Commande (Logistics)")
    idgroup = fields.Char(string="IDGROUP (Logistics)")

    @api.depends("state", "order_line.invoice_status", "order_line.qty_delivered")
    def get_delivered_state(self):
        for order in self:
            _logger.debug("Compute the delivered state for %s" % order)
            delivered = True
            for line in order.order_line:
                if line.product_id.type == "service":
                    continue
                delivered = delivered & (line.qty_delivered == line.product_uom_qty)
            #                _logger.debug("LINE DELIVERED qty_delivered %s and due %s fro product %s" % (line.qty_delivered, line.product_uom_qty, line.product_id.name ))

            order.fully_delivered = delivered
            #            _logger.debug("DELIVERED %s" % delivered)
            if order.state not in ("done", "draft", "sent") and delivered:
                order.state = "l4_shipped"

    @api.depends("state", "order_line.invoice_status")
    def _get_invoiced(self):
        """
        Compute the invoice status of a SO. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also hte default value if the conditions of no other status is met.
        - to invoice: if any SO line is 'to invoice', the whole SO is 'to invoice'
        - invoiced: if all SO lines are invoiced, the SO is invoiced.
        - upselling: if all SO lines are invoiced or upselling, the status is upselling.

        The invoice_ids are obtained thanks to the invoice lines of the SO lines, and we also search
        for possible refunds created directly from existing invoices. This is necessary since such a
        refund is not directly linked to the SO.
        """
        for order in self:
            invoice_ids = (
                order.order_line.mapped("invoice_lines")
                .mapped("move_id")
                .filtered(lambda r: r.move_type in ["out_invoice", "out_refund"])
            )
            # Search for invoices which have been 'cancelled' (filter_refund = 'modify' in
            # 'account.invoice.refund')
            # use like as origin may contains multiple references (e.g. 'SO01, SO02')
            refunds = invoice_ids.search(
                [("invoice_origin", "like", order.name)]
            ).filtered(lambda r: r.move_type in ["out_invoice", "out_refund"])
            invoice_ids |= refunds.filtered(
                lambda r: order.name
                in [
                    invoice_origin.strip()
                    for invoice_origin in r.invoice_origin.split(",")
                ]
            )
            # Search for refunds as well
            refund_ids = self.env["account.move"].browse()
            if invoice_ids:
                for inv in invoice_ids:
                    refund_ids += refund_ids.search(
                        [
                            ("move_type", "=", "out_refund"),
                            ("invoice_origin", "=", inv.sequence_number),
                            ("invoice_origin", "!=", False),
                            ("journal_id", "=", inv.journal_id.id),
                        ]
                    )

            # Ignore the status of the deposit product
            deposit_product_id = self.env[
                "sale.advance.payment.inv"
            ]._default_product_id()
            line_invoice_status = [
                line.invoice_status
                for line in order.order_line
                if line.product_id != deposit_product_id
            ]

            if order.state not in ("sale", "done", "l4_preparation", "l4_shipped"):
                invoice_status = "no"
            elif any(
                invoice_status == "to invoice" for invoice_status in line_invoice_status
            ):
                invoice_status = "to invoice"
            elif all(
                invoice_status == "invoiced" for invoice_status in line_invoice_status
            ):
                invoice_status = "invoiced"
            elif all(
                invoice_status in ["invoiced", "upselling"]
                for invoice_status in line_invoice_status
            ):
                invoice_status = "upselling"
            else:
                invoice_status = "no"

            order.update(
                {
                    "invoice_count": len(set(invoice_ids.ids + refund_ids.ids)),
                    "invoice_ids": invoice_ids.ids + refund_ids.ids,
                    "invoice_status": invoice_status,
                }
            )
