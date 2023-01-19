from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
from datetime import datetime, timedelta
import datetime as dt
import pytz
from dateutil import tz
import logging

_logger = logging.getLogger(__name__)


class HREmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    _sql_constraints = [
        ('emp_code_unique', 'unique (emp_code)', "Employee Code must be uniq."),
    ]

    emp_code = fields.Char(string="Employee Code")
    last_id = fields.Integer()
    device_id = fields.Char(string='Biometric Device ID', required=False)


class HRAttendanceInherit(models.Model):
    _inherit = 'hr.attendance'

    emp_code = fields.Char(string="Employee Code")
    check_in_sequence = fields.Integer(string="Check In Sequence")
    check_out_sequence = fields.Integer(string="Check Out Sequence")
    device_id = fields.Char(string='Biometric Device ID', required=False)


class ZkMachine(models.Model):
    _name = 'zk.machine.attendance'
    _inherit = 'hr.attendance'

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """overriding the __check_validity function for employee attendance."""
        pass

    device_id = fields.Char(string='Biometric Device ID')
    punch_type = fields.Selection([('0', 'Check In'),
                                   ('1', 'Check Out'),
                                   ('2', 'Break Out'),
                                   ('3', 'Break In'),
                                   ('4', 'Overtime In'),
                                   ('5', 'Overtime Out')],
                                  string='Punching Type')
    punching_time = fields.Datetime(string='Punching Time')


class ZKAttendance(models.Model):
    _name = 'zk.attendance'
    _rec_name = 'machine_id'
    _description = "ZK Attendance"

    machine_id = fields.Char(string="Machine")
    user_name = fields.Char(string="Username", required=True)
    password = fields.Char(string="Password", required=True)
    serial_number = fields.Char(string="Serial Number")

    @api.model
    def create(self, vals):
        res = super(ZKAttendance, self).create(vals)
        machine = self.env['zk.attendance'].sudo().search([])
        if len(machine.ids) > 1:
            raise UserError(_("Configuration already set."))
        return res

    @api.model
    def _tz_get(self):
        return [(x, x) for x in pytz.all_timezones]

    tz = fields.Selection(
        _tz_get, string='Timezone', required=True,
        help="This field is used in order to define in which timezone the machine will work.")

    def action_test_connection(self):
        self.ensure_one()
        response = self.set_connection()
        if response and response.status_code == 200:
            message = _("Connection Test Successful!")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            message = _("Test connection failed.")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': 'warning',
                    'sticky': False,
                }
            }

    def set_connection(self):
        url = self.env['ir.config_parameter'].sudo().get_param('res.config.settings.zk_url')
        if not url:
            raise UserError(_("Please Enter URL."))
        if self.user_name and self.password:
            url = url + '/api-token-auth/'
            headers = {
                'Content-Type': 'application/json'
            }
            payload = json.dumps({
                "username": str(self.user_name),
                "password": str(self.password)
            })
            try:
                response = requests.request("POST", url, headers=headers, data=payload)
                return response
            except requests.exceptions:
                raise UserError(("%s", requests.exceptions))

    # def generate_token(self):
    #     response = self.set_connection()
    #     if response and response.status_code == 200:
    #         res_dict = json.loads(response.text)
    #         return res_dict
    #     else:
    #         raise UserError(_("Connection failed"))

    # def get_machine_details(self):
    #     url = self.env['ir.config_parameter'].sudo().get_param('res.config.settings.zk_url')
    #     response = self.set_connection()
    #     if response and response.status_code == 200:
    #         res_dict = json.loads(response.text)
    #         if 'token' in res_dict:
    #             url = url + '/iclock/api/terminals/'
    #             headers = {
    #                 'Content-Type': 'application/json',
    #                 "Authorization": 'token ' + res_dict['token']
    #             }
    #             payload = json.dumps({
    #                 "username": str(self.user_name),
    #                 "password": str(self.password)
    #             })
    #             try:
    #                 response = requests.request("GET", url, headers=headers, data=payload)
    #                 return response
    #             except requests.exceptions:
    #                 raise UserError(("%s", requests.exceptions))
    #     else:
    #         raise UserError(_("Connection failed"))

    def get_attendance(self):
        if not self.tz:
            raise UserError(_("Please select Timezone."))
        _logger.info("##################Start Download Attendance#######################")
        base_url = self.env['ir.config_parameter'].sudo().get_param('res.config.settings.zk_url')
        attendance_obj = self.env['hr.attendance'].sudo()
        zk_attendance = self.env['zk.machine.attendance'].sudo()
        conn_response = self.set_connection()
        if conn_response and conn_response.status_code == 200:
            employees = self.env['hr.employee'].sudo().search([]).filtered(lambda s:s.emp_code)
            res_dict = json.loads(conn_response.text)
            if 'token' in res_dict:
                try:
                    headers = {
                        "Authorization": 'token ' + res_dict['token']
                    }
                    today = datetime.strptime(datetime.today().strftime('%Y-%m-%d 00:00:00'),
                                              '%Y-%m-%d %H:%M:%S')
                    today_last = datetime.strptime(datetime.today().strftime('%Y-%m-%d 23:59:59'),
                                                   '%Y-%m-%d %H:%M:%S')
                    for employee in employees:
                        url = base_url + '/iclock/api/transactions/?emp_code=%s&page_size=%s&start_time=%s&end_time=%s' % (
                        employee.emp_code, 9999, str(today), str(today_last))
                        response = requests.request("GET", url, headers=headers)
                        if response and response.status_code == 200:
                            att_dict = json.loads(response.text)
                            for data in att_dict['data']:
                                atten_time = datetime.strptime(str(data['punch_time']), '%Y-%m-%d %H:%M:%S')
                                atten_start_date = datetime.strptime(atten_time.strftime('%Y-%m-%d 00:00:00'),
                                                                     '%Y-%m-%d %H:%M:%S')
                                atten_end_date = datetime.strptime(atten_time.strftime('%Y-%m-%d 23:59:59'),
                                                                   '%Y-%m-%d %H:%M:%S')
                                atten_time = datetime.strptime(atten_time.strftime('%Y-%m-%d %H:%M:%S'),
                                                               '%Y-%m-%d %H:%M:%S')
                                local_tz = pytz.timezone(self.tz)
                                local_dt = local_tz.localize(atten_time, is_dst=None)
                                utc_dt = local_dt.astimezone(pytz.utc)
                                utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                                atten_time_date = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
                                atten_time = fields.Datetime.to_string(atten_time_date)
                                atten_start_date = fields.Datetime.to_string(atten_start_date)
                                atten_end_date = fields.Datetime.to_string(atten_end_date)
                                verify_type = False
                                if data['verify_type']:
                                    verify_type = str(data['verify_type'])
                                attendance_api_log_vals = {
                                    'device_id': data['id'],
                                    'emp_code': data['emp_code'],
                                    'punch_time': atten_time,
                                    'punch_state': data['punch_state'],
                                    'punch_state_display': data['punch_state_display'],
                                    'verify_type': verify_type,
                                    'verify_type_display': data['verify_type_display'],
                                    'work_code': data['work_code'],
                                    'gps_location': data['gps_location'],
                                    'area_alias': data['area_alias'],
                                    'terminal_sn': data['terminal_sn'],
                                    'temperature': data['temperature'],
                                    'is_mask': data['is_mask'],
                                    'terminal_alias': data['terminal_alias']
                                }
                                employee_id = self.env['hr.employee'].sudo().search(
                                    [('emp_code', '=', data['emp_code']), ('active', '=', True)], limit=1)

                                if employee_id:
                                    duplicate_atten_ids = zk_attendance.search(
                                        ['|', ('device_id', '=', data['id']), ('punching_time', '=', atten_time)])
                                    if duplicate_atten_ids:
                                        continue
                                    else:
                                        attendance_api_log_vals.update(
                                            {'employee_id': employee_id.id})
                                        check_status = False
                                        zk_att_day = zk_attendance.search([('employee_id', '=', employee.id),
                                                                           ('punching_time', '>=', atten_start_date),
                                                                           '|', ('punching_time', '<=', atten_end_date),
                                                                           ('punching_time', '=', False)],
                                                                          order="punching_time DESC")
                                        if not zk_att_day:
                                            check_status = '0'
                                            try:
                                                attendances_without_checkout = self.env['hr.attendance'].sudo().search(
                                                    [('employee_id', '=', employee.id,), ('check_in', '!=', False), ('check_out', '=', False)])
                                                for attendance in attendances_without_checkout:
                                                    working_time = attendance.employee_id.resource_calendar_id
                                                    if working_time:
                                                        day = attendance.check_in.weekday()
                                                        working_attendance_id = working_time.attendance_ids.filtered(lambda s:s.dayofweek == str(day) and s.day_period == 'morning')
                                                        if working_attendance_id:
                                                            hour_end = int(working_attendance_id.hour_to)
                                                            minute_end = int((working_attendance_id.hour_to * 60) % 60)
                                                            check_out_time = attendance.check_in.replace(hour=hour_end, minute=minute_end, second=00)
                                                            utc_zone = tz.gettz('UTC')
                                                            local_zone = tz.gettz('Asia/Qatar')
                                                            qatar_check_out_time = check_out_time.replace(tzinfo=local_zone).astimezone(utc_zone).strftime('%Y-%m-%d %H:%M:%S')
                                                            attendance.sudo().write({'check_out': qatar_check_out_time})
                                                        else:
                                                            check_out_time = attendance.check_in.replace(hour=17, minute=59, second=59)
                                                            qatar_check_out_time = check_out_time.astimezone(
                                                                pytz.timezone('Asia/Qatar')).replace(tzinfo=None)
                                                            attendance.sudo().write({'check_out': qatar_check_out_time})
                                                    else:
                                                        check_out_time = attendance.check_in.replace(hour=17, minute=59,
                                                                                                     second=59)
                                                        qatar_check_out_time = check_out_time.astimezone(
                                                            pytz.timezone('Asia/Qatar')).replace(tzinfo=None)
                                                        attendance.sudo().write({'check_out': qatar_check_out_time})

                                                zk_attendance_id = zk_attendance.create({'employee_id': employee.id,
                                                                                         'device_id': str(data['id']),
                                                                                         'punch_type': check_status,
                                                                                         'punching_time': atten_time})
                                                attendance_id = attendance_obj.sudo().create(
                                                    {'employee_id': employee.id, 'check_in': atten_time,
                                                     'device_id': str(data['id'])})
                                            except:
                                                pass
                                        else:
                                            if zk_att_day[0]:
                                                check_status = '1'
                                                attendance_id = attendance_obj.sudo().search([('employee_id', '=', employee.id),
                                                     ('check_in', '>=', atten_start_date),
                                                     ('check_in', '<=', atten_end_date),
                                                     ])
                                                zk_attendance_id = zk_attendance.create({'employee_id': employee.id,
                                                                                         'device_id': str(data['id']),
                                                                                         'punch_type': check_status,
                                                                                         'punching_time': atten_time})
                                                attendance_id.write({'check_out': atten_time})
                                        if attendance_id:
                                            attendance_api_log_vals.update(
                                                {'attendance_id': attendance_id.id})
                                        if zk_attendance_id:
                                            attendance_api_log_vals.update(
                                                {'zk_attendance_id': zk_attendance_id.id})
                                attendance_api_log_id = self.env['attendance.api.log'].sudo().search([(
                                    'device_id', '=', data['id']
                                )])
                                if not attendance_api_log_id:
                                    self.env['attendance.api.log'].sudo().create(attendance_api_log_vals)

                except requests.exceptions:
                    raise UserError(("%s", requests.exceptions))
        else:
            raise UserError(_("Connection failed"))
        _logger.info("##################End Download Attendance#######################")

    @api.model
    def download_attendance_cron(self):
        try:
            machine = self.env['zk.attendance'].search([])
            for rec in machine:
                rec.get_attendance()
        except:
            return False
