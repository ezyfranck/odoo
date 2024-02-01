# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _create_default_uvc(self):
        uvc_level = self.env.ref(
            "logistic_dimension_improvements.product_packaging_level_uvc"
        )
        missing_uvc_prod_ids = self.filtered(
            lambda p: p.level in ["consu", "product"]
            and uvc_level not in p.packaging_ids.mapped("packaging_level_level")
        )
        val_list = []
        for prod in missing_uvc_prod_ids:
            pack_values = {
                "packaging_level_level": uvc_level.id,
                "name": uvc_level.code,
                "uom_id": prod.uom_id.id,
                "product_id": prod.id,
                "barcode": prod.barcode or "",
                "company_id": prod.company_id.id or False,
            }
            val_list.append(pack_values)

        self.env["product.packaging"].create(val_list)

    @api.model_create_multi
    def create(self, vals_list):
        products = super(ProductProduct, self).create(vals_list)
        products._create_default_uvc()
        return products

    def write(self, values):
        res = super(ProductProduct, self).write(values)
        self._create_default_uvc()
        return res
