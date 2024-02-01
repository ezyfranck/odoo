# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID
from odoo.api import Environment


def pre_init_hook(cr):
    with Environment.manage():
        env = Environment(cr, SUPERUSER_ID, {})
        ResConfig = env["res.config.settings"]
        default_values = ResConfig.default_get(list(ResConfig.fields_get()))
        default_values.update(
            {
                "group_stock_tracking_lot": True,
                "group_stock_packaging": True,
                "group_uom": True,
            }
        )
        ResConfig.sudo().create(default_values).execute()


# group_stock_packaging /
