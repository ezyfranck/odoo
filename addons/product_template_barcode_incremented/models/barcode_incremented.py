from odoo import models, fields, api

class ProductTemplateBarcode(models.Model):
    _inherit = 'product.template'

    barcode = fields.Char(string='Barcode', default=lambda self: self._generate_barcode(), store=True)

    @api.model
    def _generate_barcode(self):
        sequence = self.env['ir.sequence'].next_by_code('product.template.barcode.sequence')
        print("Sequence:", sequence)
        return sequence
