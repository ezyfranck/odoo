# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models

LOGISTICS_BARCODE_LEVEL = [
    ("uvc", _("Sales Unit")),
    ("spcb", _("SPCB (Sub Per How Many)")),
    ("pcb", _("PCB (Per How Many)")),
    ("sup", _("SUP")),
    ("pal", _("Pallets")),
    ("nc", _("Not Concerned")),
]


class ProductPackaginglevel(models.Model):
    _inherit = "product.packaging.level"

    logistics_uom_level = fields.Selection(
        selection=LOGISTICS_BARCODE_LEVEL,
        string=_("Logistic level"),
        required=True,
        default="nc",
    )

    # TODO : create uvc when updating

    _sql_constraints = [
        (
            "unique_packaging_logistic_level",
            "unique(logistics_uom_level)",
            _("Logistic level must be unique per packaging level"),
        ),
    ]
