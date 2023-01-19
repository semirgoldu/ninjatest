from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrLeaveTypeCustom(models.Model):
    _inherit = "hr.leave.type"

    is_casual_leave_type = fields.Boolean(string="Is Casual leave type")

    @api.constrains('is_casual_leave_type','request_unit')
    def check_is_casual_leave_type(self):
        for record in self:
            if record.is_casual_leave_type and len(self.search([('is_casual_leave_type', '=', True)])) > 1:
                raise UserError(_('Casual leave type is already exist'))
            elif record.is_casual_leave_type and record.request_unit != 'hour':
                raise UserError(_('Casual leave type in taken leave must be hours'))
