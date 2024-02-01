import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

# from .stock_move import LOGISTICS_MOVE_STATE_LIST

_logger = logging.getLogger(__name__)


def _check_default_code(self, default_code, name):
    company_id = self.env.user.company_id
    if company_id.check_product_constraints:
        # TODO: check if this part could be usefull
        # if not default_code :
        #            _logger.error(_("[L4]Product %s default_code is empty.\nPlease control your product code!") % name)
        #            raise ValidationError(_("[L4]Product default_code %s is empty.\nPlease control your product code!") % (name,) )

        # Check Length
        if default_code and len(default_code) > 17:
            _logger.error(
                _(
                    "[Logistics]Product code %s is too long for logistics.\nPlease control your product code!"
                )
                % default_code
            )
            raise ValidationError(
                _(
                    "[Logistics]Product code %s is too long.\nPlease control your product code!"
                )
                % (default_code,)
            )


def _check_ean13(self, ean13, name):
    company_id = self.env.user.company_id
    if company_id.check_product_constraints:
        if not ean13:
            _logger.error(
                _(
                    "[Logistics]Product barcode %s is empty.Please control your product ean13 barcode!"
                )
                % (name,)
            )
            raise ValidationError(
                _(
                    "[Logistics]Product barcode %s is empty.\nPlease control your product EAN13!"
                )
                % (name,)
            )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    type = fields.Selection(tracking=True)

    @api.constrains(
        "name",
    )
    def _check_description_fields(self, vals=None):
        company_id = self.env.user.company_id
        if company_id.check_product_constraints:
            if len(self.name) > 30:
                _logger.error(
                    _(
                        "[Logistics]The name %s is too long for logistics. It will be truncated!"
                    )
                    % self.name
                )
                self.name = self.name[:30]


class ProductProduct(models.Model):
    _inherit = "product.product"

    refart_no_export = fields.Boolean("Don't Export in refart", default=False)

    def toggle_refart_no_export(self):
        self.ensure_one()
        self.refart_no_export = not self.refart_no_export

    @api.constrains(
        "default_code",
    )
    def _constraint_check_default_code(self):
        for product in self:
            if product.type == "product" and product.sale_ok:
                _check_default_code(product, product.default_code, product.name)

    @api.constrains("barcode")
    def _check_ean13(self):
        if self.type == "product" and self.sale_ok and self.active:
            _check_ean13(self, self.barcode, self.name)

    def _create_default_uvc(self):
        uvc_level = self.env.ref(
            "logistics_improvements.product_packaging_level_uvc"
        )
        missing_uvc_prod_ids = self.filtered(
            lambda p: p.type in ["consu", "product"]
            and uvc_level not in p.packaging_ids.mapped("packaging_level_id")
        )
        val_list = []
        for prod in missing_uvc_prod_ids:
            pack_values = {
                "packaging_level_id": uvc_level.id,
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
        # products._create_default_uvc()
        return products

    def write(self, values):
        res = super(ProductProduct, self).write(values)
        # self._create_default_uvc()
        return res