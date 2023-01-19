# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class JustificationAttendanceWizard(models.TransientModel):
    _name = 'justification.attendance.wizard'

    add_late_check_in_hour = fields.Boolean(string="Add late check in hour")
    add_early_check_out_hour = fields.Boolean(string="Add early check out hour")
    add_both = fields.Boolean(string="Both")
    is_early_check_out_hour_added = fields.Boolean(string="Is early check out hour added",default=True)
    is_late_check_in_hour_added = fields.Boolean(string="is late check in hour added",default=True)

    def refuse_justification(self):
        if self._context.get('active_id') and self._context.get('active_model') == 'hr.attendance':
            attendance = self.env['hr.attendance'].browse(self._context.get('active_id'))
            activity = self.env.ref('taqat_early_late_attandence.mail_activity_approve_attendance').id
            attendance.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).action_feedback()
            if self.add_early_check_out_hour and attendance.early_check_out_hour > 0.0 and not attendance.is_early_check_out_hour_added:
                violation_hours = attendance.employee_id.violation_hours + attendance.early_check_out_hour
                attendance.employee_id.sudo().write({'violation_hours': violation_hours})
                attendance.is_early_check_out_hour_added = True
            if self.add_late_check_in_hour and attendance.late_check_in_hour > 0.0 and not attendance.is_late_check_in_hour_added:
                violation_hours = attendance.employee_id.violation_hours + attendance.late_check_in_hour
                attendance.employee_id.sudo().write({'violation_hours': violation_hours})
                attendance.is_late_check_in_hour_added = True
            attendance.attendance_status = 'rejected'
        return True

    @api.model
    def default_get(self, fields):
        res = super(JustificationAttendanceWizard, self).default_get(fields)
        if self._context.get('active_id') and self._context.get('active_model') == 'hr.attendance':
            attendance = self.env['hr.attendance'].browse(self._context.get('active_id'))
            if not attendance.is_early_check_out_hour_added and attendance.is_early_check_out:
                res.update({'is_early_check_out_hour_added': attendance.is_early_check_out_hour_added})
            if not attendance.is_late_check_in_hour_added and attendance.is_late_check_in:
                res.update({'is_late_check_in_hour_added': attendance.is_late_check_in_hour_added})
        return res
