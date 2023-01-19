from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, time, timedelta


class HrLeaveInherit(models.Model):
    _inherit = 'hr.leave'

    replacement_employee_id = fields.Many2one('hr.employee', string="Replacement Employee")
    is_sick_leave = fields.Boolean(compute="get_is_sick_leave")
    is_manager = fields.Boolean(compute='_compute_button_visible')

    def _compute_button_visible(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.leave_manager_id and rec.employee_id.leave_manager_id.id == rec._uid or self.user_has_groups(
                    'taqat_groups_access_rights_extended.taqat_group_hr_manager_role'):
                rec.is_manager = True
            else:
                rec.is_manager = False

    @api.depends('holiday_status_id')
    def get_is_sick_leave(self):
        for rec in self:
            rec.is_sick_leave = False
            if rec.holiday_status_id and rec.holiday_status_id.is_sick_leave:
                rec.is_sick_leave = True

    # @api.model
    # def create(self, vals):
    #     res = super(HrLeaveInherit, self).create(vals)
    #     leave_type_id = self.env['hr.leave.type'].sudo().browse(vals.get('holiday_status_id'))
    #     if not vals.get('replacement_employee_id') and not leave_type_id.is_sick_leave:
    #         raise UserError(_('Please, Add Replacement Employee.'))
    #     if vals.get('replacement_employee_id') and not leave_type_id.is_sick_leave:
    #         leaves = self.env['hr.leave'].sudo().search(
    #             [('employee_id', '=', vals.get('replacement_employee_id')), ('state', '=', 'validate')])
    #         for leave in leaves:
    #             delta = leave.request_date_to - leave.request_date_from
    #             leave_days = [leave.request_date_from + timedelta(days=i) for i in
    #                           range(delta.days + 1)]
    #             replacement_leaves = self.env['hr.leave'].sudo().search(
    #             [('employee_id', '=', vals.get('replacement_employee_id')), ('state', '=', 'validate'), '|', ('request_date_from', 'in', leave_days), ('request_date_to', 'in', leave_days)])
    #             if replacement_leaves:
    #                 raise UserError(_('Replacement Employee is on Leave.'))
    #     return res

    # def write(self, vals):
    #     res = super(HrLeaveInherit, self).write(vals)
    #     leave_type_id = self.env['hr.leave.type'].sudo().browse(vals.get('holiday_status_id'))
    #     if not self.replacement_employee_id and not self.holiday_status_id.is_sick_leave:
    #         raise UserError(_('Please, Add Replacement Employee.'))
    #     if self.replacement_employee_id and not self.holiday_status_id.is_sick_leave and self.state == 'draft' or self.state == 'confirm':
    #         leaves = self.env['hr.leave'].sudo().search(
    #             [('employee_id', '=', self.replacement_employee_id.id), ('state', '=', 'validate')])
    #         for leave in leaves:
    #             delta = leave.request_date_to - leave.request_date_from
    #             leave_days = [leave.request_date_from + timedelta(days=i) for i in
    #                           range(delta.days + 1)]
    #             replacement_leaves = self.env['hr.leave'].sudo().search(
    #                 [('employee_id', '=', self.replacement_employee_id.id), ('state', '=', 'validate'), '|',
    #                  ('request_date_from', 'in', leave_days), ('request_date_to', 'in', leave_days)])
    #             if replacement_leaves:
    #                 raise UserError(_('Replacement Employee is on Leave.'))
    #     return res

    @api.onchange('holiday_status_id', 'replacement_employee_id', 'employee_ids', 'request_date_from', 'request_date_to')
    def onchange_replacement_employee(self):
        if self.holiday_status_id and self.replacement_employee_id and self.employee_ids and self.request_date_from and self.request_date_to and not self.holiday_status_id.is_sick_leave:
            leaves = self.env['hr.leave'].sudo().search(
                [('employee_id', '=', self.replacement_employee_id.id), ('state', '=', 'validate')])
            for leave in leaves:
                delta = leave.request_date_to - leave.request_date_from
                leave_delta = self.request_date_to - self.request_date_from
                leave_days = [leave.request_date_from + timedelta(days=i) for i in
                              range(delta.days + 1)]
                own_leave_days = [self.request_date_from + timedelta(days=i) for i in
                              range(leave_delta.days + 1)]
                for rec in own_leave_days:
                    if rec in leave_days:
                        self.replacement_employee_id = False
                        raise UserError(_('Replacement Employee is on Leave.'))


class HrLeaveTypeInherit(models.Model):
    _inherit = 'hr.leave.type'

    is_sick_leave = fields.Boolean(default=False, string="Is Sick Leave?")
