# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    # @api.onchange('employee_id')
    # def _onchange_employee_id(self):
    #     for rec in self:
    #         if rec.employee_id.main_project:
    #             rec.role_distribution_id = rec.employee_id.main_project.role_distribution
