# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class SaleOrderImporter(Component):
    _inherit = "prestashop.sale.order.importer"

    def _after_import(self, binding):
        super()._after_import(binding)
        self._update_lines_from_order_type_id(binding)

    def _update_lines_from_order_type_id(self, binding):
        binding.odoo_id._compute_sale_type_id()
