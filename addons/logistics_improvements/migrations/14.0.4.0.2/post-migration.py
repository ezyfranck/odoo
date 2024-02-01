# © 2017 Akretion, Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    if not version:
        return

    with api.Environment.manage():
        envr = api.Environment(env.cr, SUPERUSER_ID, {})
        id_prep = envr.ref("logistics_improvements.substate_value_preparation_to_do").id
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE stock_move
            SET substate_id = %d
            WHERE state = 'l4_preparation'
            """
            % id_prep,
        )

        id_send = envr.ref("logistics_improvements.substate_value_sent_to_logistics").id
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE stock_move
            SET substate_id = %d
            WHERE state = 'l4_sent'
            """
            % id_send,
        )

        id_refused = envr.ref(
            "logistics_improvements.substate_value_refused_by_logistics"
        ).id
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE stock_move
            SET substate_id = %d
            WHERE state = 'l4_refused'
            """
            % id_refused,
        )

        default_substate = envr.ref(
            "logistics_improvements.substate_value_ready_for_logistics"
        ).id
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE stock_move
            SET substate_id = %d
            WHERE substate_id IS NULL
            """
            % default_substate,
        )

        # PICKINGS

        id_prep = envr.ref(
            "logistics_improvements.substate_value_picking_preparation_to_do"
        ).id
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE stock_picking
            SET substate_id = %d, textual_substate = 'preparation_to_do'
            WHERE state = 'l4_preparation'
            """
            % id_prep,
        )

        id_send = envr.ref(
            "logistics_improvements.substate_value_picking_sent_to_logistics"
        ).id
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE stock_picking
            SET substate_id = %d, textual_substate = 'sent_to_logistics'
            WHERE state = 'l4_sent'
            """
            % id_send,
        )

        id_refused = envr.ref(
            "logistics_improvements.substate_value_picking_refused_by_logistics"
        ).id
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE stock_picking
            SET substate_id = %d, textual_substate = 'refused_by_logistics'
            WHERE state = 'l4_refused'
            """
            % id_refused,
        )

        default_substate = envr.ref(
            "logistics_improvements.substate_value_picking_ready_for_logistics"
        ).id
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE stock_picking
            SET substate_id = %d
            WHERE substate_id IS NULL
            """
            % default_substate,
        )

    # SALE ORDER
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order
        SET state = 'sale'
        WHERE state not in ('draft', 'sent', 'sale', 'done', 'cancel')
        """,
    )

    # Reinit state to natives
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move
        SET state = 'assigned'
        WHERE state in ('l4_sent', 'l4_preparation', 'l4_refused' )
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_line
        SET state = 'assigned'
        WHERE state in ('l4_sent', 'l4_preparation', 'l4_refused' )
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_picking
        SET state = 'assigned'
        WHERE state in ('l4_sent', 'l4_preparation', 'l4_refused' )
        """,
    )

    _logger.debug("Look for pickings with no substates")  
    
#    pickings = envr["stock.picking"].search([("substate_id", "!=", False)])
#    _logger.debug("Found %s pickings for Updating textual substates" % len(pickings))
#    move_ids = pickings.mapped("move_ids_without_package")
    
#    _logger.debug("Found %s Moves for Updating textual substates" % len(move_ids))
#    move_ids._compute_textual_state()
    
#    _logger.debug("Ensure %s pickings have proper substate" % len(pickings))
#    pickings._compute_substate()
    _logger.debug("Update done!")
