from odoo import models, fields, api, _


class HrLeaveAllocationInherit(models.Model):
    _inherit = 'hr.leave.allocation'

    is_manager = fields.Boolean(string="Manager", compute="get_is_manager")

    def get_is_manager(self):
        for rec in self:
            rec.is_manager = False
            if rec._context.get('uid'):
                user_id = self.env['res.users'].sudo().search([('id', '=', rec._context.get('uid'))])
                if (rec.create_uid.employee_ids and rec.create_uid.employee_ids.parent_id == user_id.employee_id) or user_id.has_group('hr_holidays.group_hr_holidays_manager'):
                    rec.is_manager = True
