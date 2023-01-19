from odoo import models, fields, api, _
import datetime


class TenancyRentScheduleInherit(models.Model):
    _name = 'tenancy.rent.schedule'
    _inherit = ['tenancy.rent.schedule', 'mail.thread', 'mail.activity.mixin']

    end_date = fields.Date("End Date")
    maturity_date = fields.Date("Maturity Date")
    is_deposit = fields.Boolean("Deposit")
    is_print_report = fields.Boolean("Print Report")
    bank_name = fields.Char("Bank Name")
    rent_status = fields.Selection([('pending', 'Pending'), ('returned', 'Returned'), ('done', 'Done')], 'Cheque Status')
    payment_method = fields.Selection([('cash', 'Cash'), ('wire_transfer', 'Wire Transfer'), ('cheque', 'Cheque')],
                                      'Payment Method')
    invc_id = fields.Many2one(comodel_name='account.move', string='Receipt')
    receipt_date = fields.Date(string='Receipt Date')
    old_cheques = fields.Char(string='Old Cheques')
    property_id = fields.Many2one(comodel_name='account.asset.asset', related="tenancy_id.property_id", string='Property',help='Property Name.', store=True)
    parent_id = fields.Many2one(related="property_id.parent_id", store=True)
    rel_tenant_id = fields.Many2one(comodel_name='tenant.partner', related="tenancy_id.tenant_id", string="Tenant", store=True)
    start_date = fields.Date(string='Maturity Date', help='Start Date.')
    cheque_detail = fields.Char(string='Cheque Number', size=30)


    def write(self, values):
        res = super(TenancyRentScheduleInherit, self).write(values)
        if values.get('rent_status') and values.get('rent_status') == 'returned':
            users = []
            activity_type_id = self.env.ref('taqat_property_management.mail_act_tenant_rent_schedule')
            activity_obj = self.env['mail.activity']
            users += self.env.ref('taqat_groups_access_rights_extended.taqat_group_property_employee_role').users
            for user in users:
                if self.rel_tenant_id in user.tenant_ids:
                    vals = {
                        'activity_type_id': activity_type_id.id,
                        'note': "Kindly check this return tenancy rent.",
                        'user_id': user.id,
                        'res_id': self._origin.id,
                        'res_model': 'tenancy.rent.schedule',
                        'res_model_id': self.env['ir.model'].sudo()._get('tenancy.rent.schedule').id,
                    }
                    activity_obj.sudo().create(vals)
        return res

    def check_maturity_date(self):
        tenancy = self.sudo().search([])
        today = datetime.datetime.today().date()
        tenancy = tenancy.filtered(lambda x: x.maturity_date and x.maturity_date == today)
        for rec in tenancy:
            rec.sudo().write({'rent_status': 'done', 'receipt_date': today})
