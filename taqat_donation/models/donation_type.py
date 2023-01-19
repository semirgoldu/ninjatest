from odoo import models, fields, api, _


class DonationType(models.Model):
    _name = 'donation.type'

    code = fields.Char("Code")
    name = fields.Char("Name")
    is_container = fields.Boolean("Container")
