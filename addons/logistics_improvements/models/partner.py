import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

IDCANAL = [
    ("WEB", "WEB"),
    ("PRO", "PRO"),
    ("MARKETPLACE", "MARKETPLACE"),
    ("DISTRIBUTEUR", "DISTRIBUTEUR"),
    ("REASSORT", "REASSORT"),
    ("SPECIAL", "SPECIAL"),
]


class Partner(models.Model):
    _inherit = "res.partner"

    idcanal = fields.Selection(
        selection=IDCANAL,
        string="IDCANAL (Logistics)",
        tracking=True,
        index=True,
    )
    typecmd = fields.Char(string="Type Commande (Logistics)", tracking=True)
    idgroup = fields.Char(string="IDGROUP (Logistics)", tracking=True)

    @api.model
    def create(self, vals):
        res = super(Partner, self).create(vals)
        if res.parent_id:
            res.write(
                {
                    "idcanal": res.parent_id.idcanal,
                    "typecmd": res.parent_id.typecmd,
                    "idgroup": res.parent_id.idgroup,
                }
            )
        return res

    @api.onchange("idcanal")
    def onchange_idcanal(self):
        self.typecmd = self.idcanal
        self.idgroup = False

    @api.constrains("name", "street", "street2")
    def _check_name(self):
        # Check Length
        company_id = self.env.user.company_id
        if company_id.check_partner_constraints:
            for part in self:
                if part.name and len(part.name) > 50:
                    _logger.error(
                        _(
                            """[Logistics]Name %s is too long.\n
                      Please control your name!"""
                        )
                        % part.name
                    )
                    raise ValidationError(
                        _(
                            """[Logistics]Name %s is too long.\n
                          Please control your name!"""
                        )
                        % (part.name,)
                    )
                if part.street:
                    if len(part.street) > 35:
                        _logger.error(
                            _(
                                """[Logistics]Street %s is too long.\n
                                Please control your adress!"""
                            )
                            % part.street
                        )
                        raise ValidationError(
                            _(
                                """[Logistics]Name %s is too long.\n
                                Please control your adress!"""
                            )
                            % (part.street,)
                        )
                if part.street2:
                    if len(part.street2) > 35:
                        _logger.error(
                            _(
                                """[Logistics]Street2 %s is too long.\n
                                Please control your adress!"""
                            )
                            % part.street2
                        )
                        raise ValidationError(
                            _(
                                """[Logistics]Street2 %s is too long.\n
                                Please control your adress!"""
                            )
                            % (part.street2,)
                        )
