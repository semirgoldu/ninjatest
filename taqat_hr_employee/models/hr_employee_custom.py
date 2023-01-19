from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    def get_marital_status(self):
        return [('single', 'Single'),
        ('married', 'Married'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')]

    emp_serial_number = fields.Char('Employee Number')
    marital = fields.Selection(get_marital_status, string='Marital Status', groups="hr.group_hr_user", default='single', tracking=True)

    @api.model
    def create(self, vals):
        # For Generating Sequence For Employee
        rec = super(HrEmployeeInherit, self).create(vals)
        rec.emp_serial_number = self.env['ir.sequence'].next_by_code('employee.sequence')
        return rec

    @api.onchange('parent_id')
    def onchange_all_manager(self):
        for rec in self:
            rec.env['ir.rule'].sudo().flush()
            rec.env['ir.rule'].sudo().clear_caches()

    # def state_approve(self):
    #     if any(self.document_o2m.filtered(lambda x: x.status == 'na')):
    #         raise UserError("You can't approve because in document status there is NA")
    #     else:
    #         return super(HrEmployeeInherit, self).state_approve()
