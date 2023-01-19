# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PropertyDuplicate(models.TransientModel):
    _name = 'property.duplicate'

    number_of_duplicate = fields.Integer("Duplicate")

    def duplicate(self):
        property_id = self.env['account.asset.asset'].browse(int(self._context.get('active_id')))
        for rec in range(1, self.number_of_duplicate + 1):
            copy_property = property_id.copy()
            copy_property.write({'name': property_id.name + ' - ' + str(rec)})
