# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrCustody(models.Model):
    _inherit = 'hr.employee'

    custody_count = fields.Integer(compute='_custody_count', string='# Custody')
    equipment_count = fields.Integer(compute='_equipment_count', string='# Equipments')

    # count of all custody contracts
    
    def _custody_count(self):
        for each in self:
            custody_ids = self.env['hr.custody'].search([('employee', '=', each.id)])
            each.custody_count = len(custody_ids)

    # count of all custody contracts that are in approved state
    
    def _equipment_count(self):
        for each in self:
            equipment_obj = self.env['hr.custody'].search([('employee', '=', each.id), ('state', '=', 'approved')])
            equipment_ids = []
            for each1 in equipment_obj:
                if each1.custody_name.id not in equipment_ids:
                    equipment_ids.append(each1.custody_name.id)
            each.equipment_count = len(equipment_ids)

    # smart button action for returning the view of all custody contracts related to the current employee
    
    def custody_view(self):

        action = self.env.ref('hr_custody.action_hr_custody').read([])[0]
        action['context'] = {'default_employee': self.id}
        action['domain'] = [('employee', '=', self.id)]
        return action

    # smart button action for returning the view of all custody contracts that are in approved state,
    # related to the current employee
    
    def equipment_view(self):

        action = self.env.ref('hr_custody.action_hr_custody').read([])[0]
        action['domain'] = [('employee', '=', self.id), ('state', '=', 'approved')]
        action['context'] = {'create': False,
                             'edit': False}
        return action
