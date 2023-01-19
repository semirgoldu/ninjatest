from odoo import models, fields, api, _


class TenancyInherit(models.Model):
    _inherit = 'tenant.partner'

    arabic_name = fields.Char("Arabic Name")
