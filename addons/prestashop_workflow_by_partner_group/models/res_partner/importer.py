# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class PartnerImportMapper(Component):
    _inherit = "prestashop.res.partner.mapper"
    _apply_on = "prestashop.res.partner"

    @mapping
    def fiscal_position_id(self, record):
        ps_category_id = record.get("id_default_group")
        binder = self.binder_for("prestashop.res.partner.category")
        ps_odoo_category = binder.to_internal(ps_category_id)
        position_id = self.env["account.fiscal.position"].search(
            [
                ("prestashop_partner_category", "in", ps_odoo_category.ids),
            ],
            limit=1,
        )
        _logger.debug(
            "PS: Found  %s for matching category %s" % (position_id, ps_category_id)
        )
        if len(position_id):
            return {"property_account_position_id": position_id.id}

        return {}
