# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from decimal import Decimal

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SaleOrderImporter(Component):
    _inherit = "prestashop.sale.order.importer"

    def _after_import(self, binding):
        super()._after_import(binding)
        binding._update_workflow_from_partner_category()

    def _add_shipping_line(self, binding):
        bind_partner_id = binding.commercial_partner_id.prestashop_bind_ids
        taxes_included = bind_partner_id.default_category_id.taxes_included
        shipping_total = (
            binding.total_shipping_tax_included
            if taxes_included
            else binding.total_shipping_tax_excluded
        )
        # when we have a carrier_id, even with a 0.0 price,
        # Odoo will adda a shipping line in the SO when the picking
        # is done, so we better add the line directly even when the
        # price is 0.0
        if binding.odoo_id.carrier_id:
            binding.odoo_id._create_delivery_line(
                binding.odoo_id.carrier_id, shipping_total
            )
        binding.odoo_id.recompute()


class SaleOrderLineMapper(Component):
    _inherit = "prestashop.sale.order.line.mapper"

    def _get_partner_group(self, record):
        order_adapter = self.component(
            usage="backend.adapter", model_name="prestashop.sale.order"
        )
        order = order_adapter.read(record["id_order"])
        id_customer = order.get("id_customer")
        binder = self.binder_for("prestashop.res.partner")
        ps_partner_id = binder.to_internal(id_customer)
        taxes_included = ps_partner_id.default_category_id.taxes_included
        return taxes_included

    @mapping
    def price_unit(self, record):
        super().price_unit(record)
        taxes_included = self._get_partner_group(record)

        if taxes_included:
            key = "unit_price_tax_incl"
        else:
            key = "unit_price_tax_excl"

        if record["reduction_percent"]:
            reduction = Decimal(record["reduction_percent"])
            price_percentage = 100 - reduction
            # avoid division by 0 in case of 100% discount
            if not price_percentage:
                price_unit = record[key]
                return {"price_unit": price_unit}
            price = Decimal(record[key])
            price_unit = price / ((100 - reduction) / 100)
        else:
            price_unit = record[key]

        return {"price_unit": price_unit}


class SaleOrderLineDiscountMapper(Component):
    _inherit = "prestashop.sale.order.discount.importer"

    def _get_partner_group(self, record):
        order_adapter = self.component(
            usage="backend.adapter", model_name="prestashop.sale.order"
        )
        order = order_adapter.read(record["id_order"])
        id_customer = order.get("id_customer")
        binder = self.binder_for("prestashop.res.partner")
        ps_partner_id = binder.to_internal(id_customer)
        taxes_included = ps_partner_id.default_category_id.taxes_included
        return taxes_included

    @mapping
    def price_unit(self, record):
        super().price_unit(record)
        taxes_included = self._get_partner_group(record)

        if taxes_included:
            price_unit = record["value"]
        else:
            price_unit = record["value_tax_excl"]
        if price_unit[0] != "-":
            price_unit = "-" + price_unit
        return {"price_unit": price_unit}
