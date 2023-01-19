# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar


class HRLeaveCustom(models.Model):
    _inherit = 'hr.leave'

    @api.model
    def create(self, vals):
        leave = super(HRLeaveCustom, self).create(vals)
        for rec in leave:
            if rec.holiday_status_id.is_haj_leave:
                start_date = date(rec.date_from.year, 1, 1)
                end_date = date(rec.date_from.year, 12, 31)
                leave_list = self.env['hr.leave'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('holiday_status_id', '=', rec.holiday_status_id.id),
                    ('date_from', '>=', start_date),
                    ('date_from', '<=', end_date),
                    ('state', '=', 'validate')
                ])
                if len(leave_list) > 0:
                    raise ValidationError(_("Cannot take 2 Haj Leave per year"))
        return leave


