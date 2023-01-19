from odoo import models, fields, api, _


class AttendanceApiLog(models.Model):
    _name = 'attendance.api.log'
    _description = "Attendance Api log"
    _rec_name = 'emp_code'

    device_id = fields.Char(string="Device Id")
    emp_code = fields.Char(string="Emp code")
    punch_time = fields.Datetime(string="Punch Time")
    punch_state = fields.Char(string="Punch state")
    punch_state_display = fields.Char(string="Punch state display")
    verify_type = fields.Char(string="Verify type")
    verify_type_display = fields.Char(string="Verify type display")
    work_code = fields.Char(string="Work code")
    gps_location = fields.Char(string="Gps location")
    area_alias = fields.Char(string="Area Alias")
    terminal_sn = fields.Char(string="Terminal sn")
    temperature = fields.Char(string="temperature")
    is_mask = fields.Char(string="Is Mark")
    terminal_alias = fields.Char(string="Terminal Alias")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    error = fields.Text(string="Error")
    attendance_id = fields.Many2one('hr.attendance', string="Attendance")
    zk_attendance_id = fields.Many2one('zk.machine.attendance', string="Zk Attendance")
