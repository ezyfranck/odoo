# © 2017 Akretion, Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):

    cr = env.cr
    openupgrade.update_module_names(
        cr,
        [("product_logistic_dimension", "logistic_dimension_improvements")],
        merge_modules=False,
    )
