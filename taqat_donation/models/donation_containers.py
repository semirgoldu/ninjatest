from odoo import models, fields, api, _


class DonationContainers(models.Model):
    _name = 'donation.containers'

    name = fields.Char("Name")
    name_arabic = fields.Char("Name Arabic")
    barcode = fields.Char("Barcode")
    code = fields.Char("Code")
    zone = fields.Char("Zone")
    street = fields.Char("Street")
    building_no = fields.Char("Building No")
