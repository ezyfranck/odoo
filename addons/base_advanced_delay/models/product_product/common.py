# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime as datetime_package
import logging
from datetime import datetime, timedelta

from odoo import fields, models
from odoo.addons import decimal_precision as dp
from odoo.fields import first
from odoo.tools import parse_date

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    # TODO: old_v10_strategy has to disappear ASAP
    delivery_delay_strategy = fields.Selection(
        selection=[
            # ("old_v10_strategy", "Ancienne strategy v10 TSF"),
            ("manual", "Manuelle"),
            ("based_on_forecast", "Based on forecast"),
        ],
        required=True,
        default="based_on_forecast",
        help="""
        If manual :
        * no computation is done
        If based_on_forecast:
        * Use the default_quantity_for_expected_date as quantity to be covered
        * Use the algo based on the inversion of the native prevision tool
        * Computations are not based on POL or SOL anymore, only stock.move are used (like in the native forcast view anyway)

        """,
    )
    # TODO: this one is really uggly and is supposed TDB
    # delivery_delay_auto should disappear form the basecode in favor of the strategy field
    delivery_delay_auto = fields.Boolean("Auto compute the text", default=True)
    delivery_delay_text = fields.Char(
        string="Text Delay for product",
        translate=True,
    )
    delivery_delay_quantity = fields.Float(
        "Computed Quantity for delivery text info",
        digits=dp.get_precision("Product Unit of Measure"),
        help="""
        """,
    )
    delivery_delay_date = fields.Date("Computed date for delivery text info")
    default_quantity_for_expected_date = fields.Float(
        default=1.0, string="Default Quantity for forecast computation"
    )

    def _select_seller_with_max_moq(
        self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False
    ):
        self.ensure_one()
        if date is None:
            date = fields.Date.context_today(self)
        # precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        res = self.env["product.supplierinfo"]
        sellers = self._prepare_sellers(params)
        sellers = sellers.filtered(
            lambda s: not s.company_id or s.company_id.id == self.env.company.id
        )
        for seller in sellers:
            if seller.date_start and seller.date_start > date:
                continue
            if seller.date_end and seller.date_end < date:
                continue
            if partner_id and seller.name not in [partner_id, partner_id.parent_id]:
                continue
            # if quantity is not None and float_compare(quantity_uom_seller, seller.min_qty, precision_digits=precision) == -1:
            #     continue
            if seller.product_id and seller.product_id != self:
                continue
            if not res or res.name == seller.name:
                res |= seller
        return res.sorted("price")[:1]

    def _expected_date_for_qty(
        self, quantity=False, warehouse=False, additionnal_delay=None
    ):
        # TODO: check why warehouse is not used, delete if needed
        self.ensure_one()
        _logger.debug(
            "[DELAY]Use those parameters  quantity: %s warehouse : %s additionnal_delay: %s"
            % (
                quantity,
                warehouse,
                additionnal_delay,
            )
        )
        quantity = quantity or self.default_quantity_for_expected_date or 1.0

        available_date_for_quantity = fields.Datetime.now()

        simple_products = self.filtered(
            lambda p: len(p.appropriate_bom_ids) == 0
            or all(
                bom_id.type != "phantom" and bom_id.add_potential_exception
                for bom_id in p.appropriate_bom_ids
            )
        )

        _logger.debug("[DELAY]SIMPLES Products found : %s" % simple_products)
        if len(simple_products):
            available_date_for_quantity = (
                simple_products._simple_product_expected_date_for_qty(
                    quantity=quantity, additionnal_delay=additionnal_delay
                )
            )

        # Composed products
        kit_products = self.filtered(
            lambda p: len(p.appropriate_bom_ids) != 0
            and all(bom_id.type == "phantom" for bom_id in p.appropriate_bom_ids)
        )
        _logger.debug("[DELAY]KIT Products found : %s" % kit_products)
        if len(kit_products):
            # TODO: Get factor
            additionnal_delay = kit_products.sale_delay or 0.0
            available_date_for_quantity = (
                kit_products._kit_product_expected_date_from_qty(
                    quantity_factor=quantity
                )
            ) + timedelta(days=additionnal_delay)

        other_product_ids = self - simple_products - kit_products
        _logger.debug(
            "[DELAY]Found unappropriate product for delay computation  : %s"
            % other_product_ids
        )

        return available_date_for_quantity or fields.Datetime.now()

    # TODO: To be deleted ? seems unused
    def _get_supplier_delays(self, quantity=1, with_reliability=False):
        supplier_info = self._select_seller_with_max_moq(
            partner_id=False,
            quantity=quantity,
            date=None,
            uom_id=False,
            params=False,
        )
        delay = supplier_info.delay
        if with_reliability:
            delay += supplier_info.supplier_reliability_delay

        return delay

    def _kit_product_expected_date_from_qty(self, quantity_factor, warehouse=False):
        self.ensure_one()
        available_date_for_quantity = fields.Datetime.now()

        exploded_boms = self._explode_boms()

        # extract the list of product used as bom component
        # component_products = self.env["product.product"].browse()
        component_products = {}
        for exploded_components in exploded_boms.values():
            # TODO : check dependency with proper filter
            # on BOM https://github.com/OCA/stock-logistics-warehouse/pull/1559
            for bom_component in exploded_components:
                product_id = first(bom_component).product_id
                if product_id.type != "product":
                    continue
                # component_products |= first(bom_component).product_id
                bom_factor = bom_component[1] + component_products.get(product_id, 0.0)
                component_products.update({product_id: bom_factor})

        for comp, bom_factor in component_products.items():
            _logger.debug(
                "[DELAY]Use those parameters  quantity_factor: %s bom_factor : %s "
                % (
                    quantity_factor,
                    bom_factor,
                )
            )

            available_date_for_quantity = max(
                available_date_for_quantity,
                # TODO: if additionnal delay not used there, check how its reported to the top level
                comp._simple_product_expected_date_for_qty(
                    quantity=quantity_factor * bom_factor,
                    warehouse=warehouse,
                    additionnal_delay=0,
                ),
            )

        return available_date_for_quantity

    def _simple_product_expected_date_for_qty(
        self, quantity=False, warehouse=False, additionnal_delay=None
    ):
        """_summary_
        oppposite process of _compute_qty_at_date method
        the native one is returning the quantity avialbal at a date
        here the process is to be able to give the customer the date
        when the requested quantity could be delivered
        Returns:
            available_date_for_quantity: the date when you can get the quantity
        """

        self.ensure_one()
        quantity = quantity or self.default_quantity_for_expected_date or 1.0
        order_date = fields.Datetime.now()
        if self.type != "product":
            return False

        if not warehouse:
            warehouse = self.env["stock.warehouse"].search(
                [("company_id", "=", self.env.company.id)], limit=1
            )

        wh_location_ids = warehouse.lot_stock_id.ids
        product_qties = self.with_context(warehouse=warehouse.id)
        if additionnal_delay is None:
            additionnal_delay = self.sale_delay

        supplier_info = self._select_seller_with_max_moq(
            partner_id=False,
            quantity=quantity,
            date=None,
            uom_id=False,
            params=False,
        )
        available_date_for_quantity = order_date

        if quantity <= product_qties.immediately_usable_qty:
            _logger.debug("This one is just for logging the case ")
            available_date_for_quantity += timedelta(days=additionnal_delay or 0.0)
        elif (
            quantity > product_qties.immediately_usable_qty
            and quantity <= product_qties.virtual_available
        ):
            # Integrate the immediately_usable_qty which could be negative
            # ( - is the solution to all the cases)
            # and help to manage the non reserved quantities in the next method
            residual_quantity = quantity - product_qties.immediately_usable_qty
            available_date_for_quantity = (
                self._compute_date_from_forecast_incoming_quantity(
                    self.ids, wh_location_ids, residual_quantity
                )
            )
            additionnal_delay += supplier_info.supplier_reliability_delay or 0.0
            available_date_for_quantity += timedelta(days=additionnal_delay or 0.0)
        elif quantity > product_qties.virtual_available:
            additionnal_delay += supplier_info.delay or 0.0
            additionnal_delay += supplier_info.supplier_reliability_delay or 0.0
            available_date_for_quantity += timedelta(days=additionnal_delay or 0.0)

        if not isinstance(available_date_for_quantity, datetime_package.datetime):
            available_date_for_quantity = datetime.combine(
                available_date_for_quantity, datetime.min.time()
            )
        return available_date_for_quantity

    def _compute_date_from_forecast_incoming_quantity(
        self, product_variant_ids, wh_location_ids, quantity=False
    ):
        """_summary_
        oppposite process of _compute_qty_at_date method
        the native one is returning the quantity avialbal at a date
        here the process is to be able to give the customer the date
        when the requested quantity could be delivered
        Returns:
            available_date_for_quantity: the date when you can get the quantity
        """
        quantity = quantity or self.default_quantity_for_expected_date or 1.0
        Forecast = self.env["report.stock.report_product_product_replenishment"]
        report_data = Forecast._get_report_lines(
            False, product_variant_ids, wh_location_ids
        )
        incoming = list(
            filter(
                lambda l: l.get("document_in") is not False
                and l.get("reservation") is False,
                report_data,
            )
        )
        incoming = sorted(
            incoming, key=lambda l: parse_date(self.env, l["receipt_date"])
        )
        residual_quantity = quantity
        min_covering_date = fields.Datetime.from_string(fields.Datetime.now())
        for receipt in incoming:
            if residual_quantity <= receipt.get("quantity"):
                min_covering_date = parse_date(self.env, receipt.get("receipt_date"))
                return min_covering_date
            residual_quantity -= receipt.get("quantity")

        return min_covering_date
