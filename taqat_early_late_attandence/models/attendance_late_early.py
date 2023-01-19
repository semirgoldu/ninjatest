from odoo import models, fields, api, _
from datetime import datetime
from dateutil import tz
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class HRAttendanceCustom(models.Model):
    _name = 'hr.attendance'
    _inherit = ['hr.attendance', 'mail.thread', 'mail.activity.mixin']

    is_late_check_in = fields.Boolean("Late Check In")
    is_early_check_out = fields.Boolean("Early check out")
    justification = fields.Text("Justification")
    justification_type_id = fields.Many2one("justification.type", "Justification Type")
    attendance_status = fields.Selection([
        ('department_manager_approve', 'Department Manager'),
        ('hr_manager', 'HR Manager'),
        ('approved', 'Approved'), ('rejected', 'Rejected')], string='Activity State',
        default='department_manager_approve')
    early_check_out_hour = fields.Float(string="Early check out hour")
    late_check_in_hour = fields.Float(string="Late check in hour")
    is_early_check_out_hour_added = fields.Boolean(string="Is early check out hour added")
    is_late_check_in_hour_added = fields.Boolean(string="is late check in hour added")
    leave_id = fields.Many2one('hr.leave', string="Leave")

    @api.model
    def create(self, vals):
        rec = super(HRAttendanceCustom, self).create(vals)
        self.get_late_checkin_attendance(rec.employee_id)
        return rec

    # def write(self, vals):
    #     res =  super(HRAttendanceCustom, self).write(vals)
    #     if vals.get('check_in'):
    #         self.get_late_checkin_attendance(self.employee_id)
    #     return res

    def get_late_checkin_attendance(self, employee):
        # all_employees = self.env['hr.employee'].search([])
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(self._context.get('tz'))
        utc = datetime.strptime(str(datetime.today()), '%Y-%m-%d %H:%M:%S.%f')
        utc = utc.replace(tzinfo=from_zone)
        central = utc.astimezone(to_zone)

        all_today_attendance = self.env['hr.attendance'].search([('check_in', '>=', datetime.strptime(
            central.strftime('%Y-%m-%d') + ' 00:00:01', '%Y-%m-%d %H:%M:%S')),
                                                                 ('check_in', '<=', datetime.strptime(
                                                                     central.strftime('%Y-%m-%d') + ' 23:59:59',
                                                                     '%Y-%m-%d %H:%M:%S'))], order='check_in asc')
        employee_attendaces = all_today_attendance.filtered(lambda x: x.employee_id == employee)
        if employee_attendaces:
            attendance_checkin_utc = datetime.strptime(str(employee_attendaces[0].check_in), '%Y-%m-%d %H:%M:%S')
            attendance_checkin_utc = attendance_checkin_utc.replace(tzinfo=from_zone)
            attendance_checkin_central = attendance_checkin_utc.astimezone(to_zone)
            data_morning = employee_attendaces[0].employee_id.resource_calendar_id.attendance_ids.filtered(
                lambda x: dict(x._fields['dayofweek'].selection).get(x.dayofweek) == central.strftime('%A') and dict(
                    x._fields['day_period'].selection).get(x.day_period) == 'Morning')
            if attendance_checkin_central.time().hour + (
                    attendance_checkin_central.time().minute / 60) > data_morning.hour_from:
                today_date_time = attendance_checkin_central.replace(hour=0, minute=0, second=0)
                leave = self.env['hr.leave'].sudo().search([('employee_id', '=', employee_attendaces[0].employee_id.id),
                                                            ('date_from', '>=', today_date_time),
                                                            ('date_to', '<=', attendance_checkin_utc),
                                                            ('state', '=', 'validate'),
                                                            ('request_unit_hours', '=', True)])
                diff = attendance_checkin_central.time().hour + (
                        attendance_checkin_central.time().minute / 60) - data_morning.hour_from
                if leave:
                    employee_attendaces[0].leave_id = leave.id
                    if diff > leave.number_of_days:
                        remaining_diff_after_leave = diff - leave.number_of_hours_display
                        employee_attendaces[0].late_check_in_hour = remaining_diff_after_leave
                        employee_attendaces[0].is_late_check_in = True
                        employee_attendaces[0].is_late_check_in_hour_added = False
                        manager_id = employee_attendaces[0].employee_id.parent_id
                        if manager_id:
                            employee_attendaces[0].activity_schedule(
                                'taqat_early_late_attandence.mail_activity_approve_attendance',
                                user_id=manager_id.user_id.id)
                else:
                    employee_attendaces[0].late_check_in_hour = diff
                    employee_attendaces[0].is_late_check_in = True
                    employee_attendaces[0].is_late_check_in_hour_added = False
                    manager_id = employee_attendaces[0].employee_id.parent_id
                    if manager_id:
                        employee_attendaces[0].activity_schedule(
                            'taqat_early_late_attandence.mail_activity_approve_attendance',
                            user_id=manager_id.user_id.id)

    def schedule_get_attendance(self):
        all_employees = self.env['hr.employee'].search([])
        for employee in all_employees:
            from_zone = tz.gettz('UTC')
            if employee.user_id.tz:
                to_zone = tz.gettz(employee.user_id.tz)
            else:
                to_zone = tz.gettz(self._context.get('tz'))
            utc = datetime.strptime(str(datetime.today() + relativedelta(days=-1)), '%Y-%m-%d %H:%M:%S.%f')
            utc = utc.replace(tzinfo=from_zone)
            central = utc.astimezone(to_zone)
            employee_attendaces = self.env['hr.attendance'].search(
                [('employee_id', '=', employee.id), ('check_out', '>=', datetime.strptime(
                    central.strftime('%Y-%m-%d') + ' 00:00:01', '%Y-%m-%d %H:%M:%S')),
                 ('check_out', '<=', datetime.strptime(
                     central.strftime('%Y-%m-%d') + ' 23:59:59',
                     '%Y-%m-%d %H:%M:%S'))], order='check_in asc')
            # employee_attendaces = all_today_attendance.filtered(lambda x: x.employee_id == employee)
            if employee_attendaces:
                if employee_attendaces[-1].check_out:
                    attendance_checkout_utc = datetime.strptime(str(employee_attendaces[-1].check_out),
                                                                '%Y-%m-%d %H:%M:%S')
                    attendance_checkout_utc = attendance_checkout_utc.replace(tzinfo=from_zone)
                    attendance_checkout_central = attendance_checkout_utc.astimezone(to_zone)
                evening_data = employee_attendaces[-1].employee_id.resource_calendar_id.attendance_ids.filtered(
                    lambda x: dict(x._fields['dayofweek'].selection).get(x.dayofweek) == central.strftime(
                        '%A') and dict(
                        x._fields['day_period'].selection).get(x.day_period) == 'Afternoon')
                if employee_attendaces[-1].check_out and attendance_checkout_central.time().hour + (
                        attendance_checkout_central.time().minute / 60) < evening_data.hour_to:
                    test = employee_attendaces[-1].check_out and \
                           attendance_checkout_central.time().hour + (attendance_checkout_central.time().minute / 60)
                    diff = evening_data.hour_to - test
                    today_date_time = attendance_checkout_central.replace(hour=int(evening_data.hour_to), minute=59,
                                                                          second=59)
                    leave = self.env['hr.leave'].sudo().search(
                        [('employee_id', '=', employee_attendaces[-1].employee_id.id),
                         ('date_from', '>=', attendance_checkout_utc),
                         ('date_to', '<=', today_date_time),
                         ('state', '=', 'validate'),
                         ('request_unit_hours', '=', True)])
                    if leave:
                        employee_attendaces[-1].leave_id = leave.id
                        leave_date_from = leave.date_from.astimezone(to_zone)
                        leave_date_to = leave.date_to.astimezone(to_zone)
                        if leave_date_from > attendance_checkout_utc:
                            attendance_checkout_hour = employee_attendaces[-1].check_out and \
                                                       attendance_checkout_utc.time().hour + (
                                                               attendance_checkout_utc.time().minute / 60)
                            leave_hour = leave.date_from and leave.date_from.time().hour + (
                                        leave.date_from.time().minute / 60)
                            remaining_diff_after_leave = leave_hour - attendance_checkout_hour
                            employee_attendaces[-1].is_early_check_out = True
                            employee_attendaces[-1].is_early_check_out_hour_added = False
                            employee_attendaces[-1].early_check_out_hour = remaining_diff_after_leave
                            manager_id = employee_attendaces[0].employee_id.parent_id
                            if manager_id:
                                employee_attendaces[0].activity_schedule(
                                    'taqat_early_late_attandence.mail_activity_approve_attendance',
                                    user_id=manager_id.user_id.id)
                    else:
                        employee_attendaces[-1].is_early_check_out = True
                        employee_attendaces[-1].is_early_check_out_hour_added = False
                        employee_attendaces[-1].early_check_out_hour = diff
                        manager_id = employee_attendaces[0].employee_id.parent_id
                        if manager_id:
                            employee_attendaces[0].activity_schedule(
                                'taqat_early_late_attandence.mail_activity_approve_attendance',
                                user_id=manager_id.user_id.id)


    def action_department_manager_approve(self):
        if self.env.user.id == self.employee_id.parent_id.user_id.id:
            if self.is_early_check_out_hour_added:
                violation_hours = self.employee_id.violation_hours - self.early_check_out_hour
                self.employee_id.sudo().write({'violation_hours': violation_hours})
            if self.is_late_check_in_hour_added:
                violation_hours = self.employee_id.violation_hours - self.late_check_in_hour
                self.employee_id.sudo().write({'violation_hours': violation_hours})
            activity = self.env.ref('taqat_early_late_attandence.mail_activity_approve_attendance').id
            self.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).action_feedback()
            self.attendance_status = 'approved'
            self.is_early_check_out_hour_added = True
            self.is_late_check_in_hour_added = True
        else:
            raise UserError("Only Employee Manager Can Approve.")


    def action_hr_manager_validate(self):
        activity = self.env.ref('taqat_early_late_attandence.mail_activity_approve_attendance').id
        self.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).action_feedback()
        self.attendance_status = 'approved'


    def _get_user_approval_activities(self, user, activity_type_id):
        domain = [
            ('res_model', '=', 'hr.attendance'),
            ('res_id', 'in', self.ids),
            ('activity_type_id', '=', activity_type_id),
            ('user_id', '=', user.id)
        ]
        activities = self.env['mail.activity'].search(domain)
        return activities


    def action_manager_refuse(self):
        if self.env.user.id == self.employee_id.parent_id.user_id.id:
            action = self.env.ref('taqat_early_late_attandence.action_justification_attendance_wizard').read()[0]
            return action
        else:
            raise UserError("Only Employee Manager Can Refuse.")


class JustificationType(models.Model):
    _name = 'justification.type'

    def default_justification_type(self):
        justification_types = self.search([('default_justification_type', '=', True)])
        if justification_types:
            return False
        return True

    def default_affects_casual_leave(self):
        casual_leave_type = self.env['hr.leave.type'].search([('is_casual_leave_type','=',True)])
        if casual_leave_type:
            return True
        else:
            return False

    name = fields.Char("Name")
    operation = fields.Selection([('gt', '>'), ('lt', '<'), ('between', 'Between')], string="Operation", default=">")
    category = fields.Selection([('official', 'Official'), ('personal', 'Personal')], string="Category",
                                default="official")
    from_time = fields.Float(string="From time")
    to_time = fields.Float(string="To time")
    affects_attendance = fields.Boolean(string="Affects Attendance")
    affects_casual_leave = fields.Boolean(string="Affects Casual Leave",default=default_affects_casual_leave)
    payroll_salary = fields.Selection(
        [('does_not_affect', 'Does not affect'),
         ('after_leave_balance_consumed', 'after leave balance is consumed'),
         ('affects_payroll', 'affects payroll')])
    default_justification_type = fields.Boolean(string="Default justification type",
                                                default=default_justification_type)
    code = fields.Char("Char")
    # duration = fields.Float(string="Duration", compute="compute_duration")
    #
    # @api.depends('from_time', 'to_time')
    # def compute_duration(self):
    #     for record in self:
    #         if record.from_time > record.to_time:
    #             record.duration = record.from_time - record.to_time
    #         elif record.to_time > record.from_time:
    #             record.duration = record.to_time - record.from_time
