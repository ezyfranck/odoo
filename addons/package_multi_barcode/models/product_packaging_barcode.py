# © 2012-2014 Guewen Baconnier (Camptocamp SA)
# © 2015 Roberto Lizana (Trey)
# © 2016 Pedro M. Baeza
# © 2018 Xavier Jimenez (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductPackagingBarcode(models.Model):
    _name = "product.packaging.barcode"
    _description = "Individual item in a packaging's barcode list"
    _order = "sequence, id"

    name = fields.Char(
        string="Barcode",
        required=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=0,
    )
    packaging_id = fields.Many2one(
        string="Product Packaging",
        comodel_name="product.packaging",
        # compute="_compute_package",
        store=True,
        readonly=False,
    )

    # product_tmpl_id = fields.Many2one(
    #     comodel_name="product.template",
    #     compute="_compute_product_tmpl",
    #     store=True,
    #     readonly=False,
    # )

    # @api.depends("product_id")
    # def _compute_product_tmpl(self):
    #     for rec in self.filtered(lambda x: not x.product_tmpl_id and x.product_id):
    #         rec.product_tmpl_id = rec.product_id.product_tmpl_id

    # @api.depends("product_tmpl_id.product_variant_ids")
    # def _compute_product(self):
    #     for rec in self.filtered(
    #         lambda x: not x.product_id and x.product_tmpl_id.product_variant_ids
    #     ):
    #         rec.product_id = rec.product_tmpl_id.product_variant_ids[0]

    @api.constrains("name")
    def _check_duplicates(self):
        for record in self:
            barcodes = self.search(
                [("id", "!=", record.id), ("name", "=", record.name)]
            )
            if barcodes:
                raise UserError(
                    _('The Barcode "%s" already exists for package ' '"%s"')
                    % (record.name, barcodes[0].packaging_id.name)
                )
