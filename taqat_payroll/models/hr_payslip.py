import base64

from odoo import models, fields, api, _
from datetime import datetime


class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _inherit = ['hr.payslip.run', 'mail.thread', 'mail.activity.mixin']

    state = fields.Selection(selection_add=[('approve', 'Approved'),
                                            ('by_hr', 'Approved by HR'),
                                            ('by_finance', 'Approved By Finance'), ('close',)])
    employee_type = fields.Selection([('fos_employee', 'Outsourced Employee'),
                                      ('fusion_employee', 'Main Company Employee'),
                                      ], string="Employee Type")

    is_finance_approve = fields.Boolean("Is Finance Approve", copy=False)

    def action_validate(self):
        res = super(HrPayslipRun, self).action_validate()
        self.state = 'by_finance'
        return res

    # def compute_sheet(self):
    #     # res = super(HrPayslipInherit, self).compute_sheet()
    #     if self.employee_type == 'fos_employee':
    #         users = []
    #         activity_to_do = self.env.ref('taqat_payroll.mail_act_payroll').id
    #         model_id = self.env['ir.model']._get('hr.payslip.run').id
    #         activity = self.env['mail.activity']
    #         users += self.env.ref('taqat_groups_access_rights_extended.group_operational_manager').users
    #         for user in users:
    #             if user.id != self.env.ref('base.user_admin').id:
    #                 act_dct = {
    #                     'activity_type_id': activity_to_do,
    #                     'note': "kindly check this Employee Payslip.",
    #                     'user_id': user.id,
    #                     'res_id': self.id,
    #                     'res_model': 'hr.payslip.run',
    #                     'res_model_id': model_id,
    #                     'date_deadline': datetime.today().date()
    #                 }
    #                 activity.sudo().create(act_dct)
    #         self.state = 'draft'
    #     elif self.employee_type == 'fusion_employee':
    #         activity_to_do = self.env.ref('taqat_payroll.mail_act_payroll').id
    #         model_id = self.env['ir.model']._get('hr.payslip.run').id
    #         activity = self.env['mail.activity']
    #         users = self.env['res.users'].search([])
    #         for user in users:
    #             if user.has_group('account.group_account_manager') and \
    #                     user.has_group('ebs_lb_payroll.group_finance_payroll_confirm') and \
    #                     not  user.id != self.env.ref('base.user_admin').id:
    #                 act_dct = {
    #                     'activity_type_id': activity_to_do,
    #                     'note': "kindly check this Employee Payslip.",
    #                     'user_id': user.id,
    #                     'res_id': self.id,
    #                     'res_model': 'hr.payslip.run',
    #                     'res_model_id': model_id,
    #                     'date_deadline': datetime.today().date()
    #                 }
    #                 activity.sudo().create(act_dct)
    #         self.direct_approved()
    #         self.action_hr_confirm()
    #
    #     # return res

    def direct_approved(self):
        if self.employee_type == 'fos_employee':
            users = []
            activity_to_do = self.env.ref('taqat_payroll.mail_act_payroll').id
            previous_activity_users = []
            previous_activity_users += self.env.ref(
                'taqat_groups_access_rights_extended.group_operational_manager').users.ids
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id), ('user_id', 'in', previous_activity_users),
                 ('activity_type_id', '=', activity_to_do)])
            activity_id.action_feedback(feedback='Approved')

            model_id = self.env['ir.model']._get('hr.payslip.run').id
            activity = self.env['mail.activity']
            users += self.env.ref('taqat_groups_access_rights_extended.group_employability_manager_role').users
            for user in users:
                if user.id != self.env.ref('base.user_admin').id:
                    act_dct = {
                        'activity_type_id': activity_to_do,
                        'note': "kindly check this Employee Payslip.",
                        'user_id': user.sudo().id,
                        'res_id': self.sudo().id,
                        'res_model': 'hr.payslip.run',
                        'res_model_id': model_id,
                        'date_deadline': datetime.today().date()
                    }
                    activity.with_context(mail_create_nosubscribe=True, mail_notrack=True, mail_activity_quick_update=True).sudo().create(act_dct)
            self.state = 'approve'
            self.is_finance_approve = False
        else:
            activity_to_do = self.env.ref('taqat_payroll.mail_act_payroll').id
            model_id = self.env['ir.model']._get('hr.payslip.run').id
            activity = self.env['mail.activity']
            users = self.env['res.users'].search([])
            for user in users:
                if user.has_group('taqat_groups_access_rights_extended.taqat_group_accounting_manager_role') and user.id != self.env.ref(
                    'base.user_admin').id:
                    act_dct = {
                        'activity_type_id': activity_to_do,
                        'note': "kindly check this Employee Payslip.",
                        'user_id': user.id,
                        'res_id': self.id,
                        'res_model': 'hr.payslip.run',
                        'res_model_id': model_id,
                        'date_deadline': datetime.today().date()
                    }
                    activity.with_context(mail_create_nosubscribe=True, mail_notrack=True, mail_activity_quick_update=True).create(act_dct)
            self.action_hr_confirm()

    def action_finance_confirm(self):
        if self.employee_type == 'fos_employee':
            users = []
            activity_to_do = self.env.ref('taqat_payroll.mail_act_payroll').id
            previous_activity_all_users = self.env['res.users'].search([])
            previous_activity_users = []
            for user in previous_activity_all_users:
                if user.has_group('taqat_groups_access_rights_extended.taqat_group_accounting_manager_role') and user.id != self.env.ref(
                    'base.user_admin').id:
                    previous_activity_users.append(user.id)
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id), ('user_id', 'in', previous_activity_users),
                 ('activity_type_id', '=', activity_to_do)])
            activity_id.action_feedback(feedback='Approved')
            model_id = self.env['ir.model']._get('hr.payslip.run').id
            activity = self.env['mail.activity']
            users += self.env.ref('ebs_lb_payroll.group_director_payroll_confirm').users
            for user in users:
                if user.id != self.env.ref('base.user_admin').id:
                    act_dct = {
                        'activity_type_id': activity_to_do,
                        'note': "kindly check this Employee Payslip.",
                        'user_id': user.id,
                        'res_id': self.id,
                        'res_model': 'hr.payslip.run',
                        'res_model_id': model_id,
                        'date_deadline': datetime.today().date()
                    }
                    activity.with_context(mail_create_nosubscribe=True, mail_notrack=True, mail_activity_quick_update=True).sudo().create(act_dct)
            self.state = 'by_finance'
            self.action_validate()
            self.is_finance_approve = False

        elif self.employee_type == 'fusion_employee':
            users = []
            activity_to_do = self.env.ref('taqat_payroll.mail_act_payroll').id
            previous_activity_all_users = self.env['res.users'].search([])
            previous_activity_users = []
            for user in previous_activity_all_users:
                if user.has_group('taqat_groups_access_rights_extended.taqat_group_accounting_manager_role') and user.id != self.env.ref(
                    'base.user_admin').id:
                    previous_activity_users.append(user.id)
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id), ('user_id', 'in', previous_activity_users),
                 ('activity_type_id', '=', activity_to_do)])
            activity_id.action_feedback(feedback='Approved')
            model_id = self.env['ir.model']._get('hr.payslip.run').id
            activity = self.env['mail.activity']
            users += self.env.ref('ebs_lb_payroll.group_director_payroll_confirm').users
            for user in users:
                if user.id != self.env.ref('base.user_admin').id:
                    act_dct = {
                        'activity_type_id': activity_to_do,
                        'note': "kindly check this Employee Payslip.",
                        'user_id': user.id,
                        'res_id': self.id,
                        'res_model': 'hr.payslip.run',
                        'res_model_id': model_id,
                        'date_deadline': datetime.today().date()
                    }
                    activity.with_context(mail_create_nosubscribe=True, mail_notrack=True, mail_activity_quick_update=True).sudo().create(act_dct)
            self.state = 'by_finance'
            self.action_validate()
            self.is_finance_approve = False

    def action_hr_confirm(self):
        if self.employee_type == 'fos_employee':
            activity_to_do = self.env.ref('taqat_payroll.mail_act_payroll').id
            previous_activity_users = []
            previous_activity_users += self.env.ref(
                'taqat_groups_access_rights_extended.group_employability_manager_role').users.ids
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id), ('user_id', 'in', previous_activity_users),
                 ('activity_type_id', '=', activity_to_do)])
            activity_id.action_feedback(feedback='Approved')
            model_id = self.env['ir.model']._get('hr.payslip.run').id
            activity = self.env['mail.activity']
            users = self.env['res.users'].search([])
            for user in users:
                if user.has_group('taqat_groups_access_rights_extended.taqat_group_accounting_manager_role') and user.id != self.env.ref(
                    'base.user_admin').id:
                    act_dct = {
                        'activity_type_id': activity_to_do,
                        'note': "kindly check this Employee Payslip.",
                        'user_id': user.id,
                        'res_id': self.id,
                        'res_model': 'hr.payslip.run',
                        'res_model_id': model_id,
                        'date_deadline': datetime.today().date()
                    }
                    activity.with_context(mail_create_nosubscribe=True, mail_notrack=True, mail_activity_quick_update=True).sudo().create(act_dct)
            self.state = 'by_hr'
            self.is_finance_approve = True
        elif self.employee_type == 'fusion_employee':
            activity_to_do = self.env.ref('taqat_payroll.mail_act_payroll').id
            previous_activity_users = []
            previous_activity_users += self.env.ref(
                'taqat_groups_access_rights_extended.taqat_group_accounting_manager_role').users.ids
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id), ('user_id', 'in', previous_activity_users),
                 ('activity_type_id', '=', activity_to_do)])
            activity_id.action_feedback(feedback='Approved')
            model_id = self.env['ir.model']._get('hr.payslip.run').id
            activity = self.env['mail.activity']
            users = self.env['res.users'].search([])
            for user in users:
                if user.has_group('taqat_groups_access_rights_extended.taqat_group_accounting_manager_role') and user.id != self.env.ref(
                    'base.user_admin').id:
                    act_dct = {
                        'activity_type_id': activity_to_do,
                        'note': "kindly check this Employee Payslip.",
                        'user_id': user.id,
                        'res_id': self.id,
                        'res_model': 'hr.payslip.run',
                        'res_model_id': model_id,
                        'date_deadline': datetime.today().date()
                    }
                    activity.with_context(mail_create_nosubscribe=True, mail_notrack=True, mail_activity_quick_update=True).sudo().create(act_dct)
            self.state = 'by_hr'
            self.is_finance_approve = True

        # return res

    def director_approved(self):
        # res = super(HrPayslipInherit, self).director_approved()
        if self.employee_type == 'fos_employee':
            activity_to_do = self.env.ref('taqat_payroll.mail_act_payroll').id
            previous_activity_users = []
            previous_activity_users += self.env.ref('ebs_lb_payroll.group_director_payroll_confirm').users.ids
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id), ('user_id', 'in', previous_activity_users),
                 ('activity_type_id', '=', activity_to_do)])
            activity_id.action_feedback(feedback='Approved')

            model_id = self.env['ir.model']._get('hr.payslip.run').id
            activity = self.env['mail.activity']
            users = self.env['res.users'].search([])
            for user in users:
                if user.has_group('taqat_groups_access_rights_extended.taqat_group_accounting_manager_role') and user.id != self.env.ref(
                    'base.user_admin').id:
                    act_dct = {
                        'activity_type_id': activity_to_do,
                        'note': "kindly Mark as paid to this Employee.",
                        'user_id': user.id,
                        'res_id': self.id,
                        'res_model': 'hr.payslip.run',
                        'res_model_id': model_id,
                        'date_deadline': datetime.today().date()
                    }
                    activity.with_context(mail_create_nosubscribe=True, mail_notrack=True, mail_activity_quick_update=True).sudo().create(act_dct)
            self.state = 'close'
            self.is_finance_approve = False
        elif self.employee_type == 'fusion_employee':
            activity_to_do = self.env.ref('taqat_payroll.mail_act_payroll').id
            previous_activity_users = []
            previous_activity_users += self.env.ref('ebs_lb_payroll.group_director_payroll_confirm').users.ids
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id), ('user_id', 'in', previous_activity_users),
                 ('activity_type_id', '=', activity_to_do)])
            activity_id.action_feedback(feedback='Approved')

            model_id = self.env['ir.model']._get('hr.payslip.run').id
            activity = self.env['mail.activity']
            users = self.env['res.users'].search([])
            for user in users:
                if user.has_group('taqat_groups_access_rights_extended.taqat_group_accounting_manager_role') and user.id != self.env.ref(
                    'base.user_admin').id:
                    act_dct = {
                        'activity_type_id': activity_to_do,
                        'note': "kindly Mark as paid to this Employee.",
                        'user_id': user.id,
                        'res_id': self.id,
                        'res_model': 'hr.payslip.run',
                        'res_model_id': model_id,
                        'date_deadline': datetime.today().date()
                    }
                    activity.with_context(mail_create_nosubscribe=True, mail_notrack=True, mail_activity_quick_update=True).sudo().create(act_dct)
            self.state = 'close'
            self.is_finance_approve = False
        # return res

    def action_payslip_paid(self):
        res = super(HrPayslipRun, self).action_payslip_paid()
        if self.employee_id.employee_type == 'fos_employee':
            activity_to_do = self.env.ref('taqat_payroll.mail_act_payroll').id
            previous_activity_all_users = self.env['res.users'].search([])
            previous_activity_users = []
            for user in previous_activity_all_users:
                if user.has_group('taqat_groups_access_rights_extended.taqat_group_accounting_manager_role') and user.id != self.env.ref(
                    'base.user_admin').id:
                    previous_activity_users.append(user.id)
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id), ('user_id', 'in', previous_activity_users),
                 ('activity_type_id', '=', activity_to_do)])
            activity_id.action_feedback(feedback='Approved')
        elif self.employee_id.employee_type == 'fusion_employee':
            activity_to_do = self.env.ref('taqat_payroll.mail_act_payroll').id
            previous_activity_all_users = self.env['res.users'].search([])
            previous_activity_users = []
            for user in previous_activity_all_users:
                if user.has_group('taqat_groups_access_rights_extended.taqat_group_accounting_manager_role') and user.id != self.env.ref(
                    'base.user_admin').id:
                    previous_activity_users.append(user.id)
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id), ('user_id', 'in', previous_activity_users),
                 ('activity_type_id', '=', activity_to_do)])
            activity_id.action_feedback(feedback='Approved')
        return res

    def send_payslips_to_employees(self):
        for payslip in self.slip_ids:
            report_template_id = self.env.ref('hr_payroll.action_report_payslip')._render_qweb_pdf(payslip.id)
            data_record = base64.b64encode(report_template_id[0])
            attachment_id = self.env['ir.attachment'].create({
                'name': payslip.sudo().name,
                'mimetype': 'application/pdf',
                'type': 'binary',
                'datas': data_record,
                'public': True,
            })
            mail = self.env['mail.mail'].sudo().create({
                'email_from': self.env.company.catchall_formatted or self.env.company.email_formatted,
                'email_to': payslip.sudo().employee_id.work_email,
                'subject': 'Payslip Info',
                'body_html': '''<div style="margin: 0px; padding: 0px;">
                            <p style="margin: 0px; padding: 0px; font-size: 13px;">
                                Dear %s,<br/><br/>
                                Your Payslip report from %s to %s
                            </p>
                            <p>
    
                                <br/>
                                Thank you.
                            </p>
                        </div>''' % ((payslip.sudo().employee_id.name), (payslip.date_from), (payslip.date_to)),
                'attachment_ids': [(6, 0, [attachment_id.id])],
            })
            mail.sudo().send()


class HrPayslipemployeesInherit(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.onchange("structure_id")
    def onchange_get_related_employees(self):
        print("self.structure_idself.structure_id",self.structure_id)
        if self.structure_id:
            employee_ids = self.env['hr.employee'].search([('contract_ids.structure_type_id.struct_ids', '=', self.structure_id.id)])
            self.write({'employee_ids': [(6, 0, employee_ids.ids)]})

    def compute_sheet(self):
        res = super(HrPayslipemployeesInherit, self).compute_sheet()
        payslip_run = self.env['hr.payslip.run'].browse(self._context.get('active_id'))
        if payslip_run.employee_type == 'fos_employee':
            users = []
            activity_to_do = self.env.ref('taqat_payroll.mail_act_payroll').id
            model_id = self.env['ir.model']._get('hr.payslip.run').id
            activity = self.env['mail.activity']
            users += self.env.ref('taqat_groups_access_rights_extended.group_operational_manager').users
            for user in users:
                if user.id != self.env.ref('base.user_admin').id:
                    act_dct = {
                        'activity_type_id': activity_to_do,
                        'note': "kindly check this Employee Payslip.",
                        'user_id': user.id,
                        'res_id': payslip_run.id,
                        'res_model': 'hr.payslip.run',
                        'res_model_id': model_id,
                        'date_deadline': datetime.today().date()
                    }
                    activity.with_context(mail_create_nosubscribe=True, mail_notrack=True, mail_activity_quick_update=True).sudo().create(act_dct)
            # self.state = 'confirm'
        # elif payslip_run.employee_type == 'fusion_employee':
            # activity_to_do = self.env.ref('taqat_payroll.mail_act_payroll').id
            # model_id = self.env['ir.model']._get('hr.payslip.run').id
            # activity = self.env['mail.activity']
            # users = self.env['res.users'].search([])
            # for user in users:
            #     if user.has_group('account.group_account_manager') and user.has_group(
            #             'ebs_lb_payroll.group_finance_payroll_confirm') and user.id != self.env.ref(
            #             'base.user_admin').id:
            #         act_dct = {
            #             'activity_type_id': activity_to_do,
            #             'note': "kindly check this Employee Payslip.",
            #             'user_id': user.id,
            #             'res_id': payslip_run.id,
            #             'res_model': 'hr.payslip.run',
            #             'res_model_id': model_id,
            #             'date_deadline': datetime.today().date()
            #         }
            #         activity.sudo().create(act_dct)
            # payslip_run.direct_approved()
            # payslip_run.action_hr_confirm()

        return res


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    is_payroll_hour = fields.Boolean(string="Payroll Period")

    def compute_sheet(self):
        res = super(HrPayslipInherit, self).compute_sheet()
        for payslip in self:
            if payslip.is_payroll_hour and payslip.date_from and payslip.date_to and payslip.contract_id:
                days = (payslip.date_to - payslip.date_from).days + 1
                hours = payslip.contract_id.resource_calendar_id.payroll_hours
                lines = []
                if days and hours > 0:
                    for line in payslip._get_payslip_lines():
                        amount = line['amount']/hours * days
                        line['amount'] = amount
                        lines.append((0, 0, line))
                    payslip.sudo().write({'line_ids': (5, 0, 0)})
                    payslip.sudo().write({'line_ids': lines})
        return res

    def send_payslip_to_employee(self):
        report_template_id = self.env.ref('hr_payroll.action_report_payslip')._render_qweb_pdf(self.id)
        data_record = base64.b64encode(report_template_id[0])

        attachment_id = self.env['ir.attachment'].create({
            'name': self.name,
            'mimetype': 'application/pdf',
            'type': 'binary',
            'datas': data_record,
            'public': True,
        })
        mail = self.env['mail.mail'].sudo().create({
            'email_from': self.env.company.catchall_formatted or self.env.company.email_formatted,
            'email_to': self.employee_id.work_email,
            'subject': 'Payslip Info',
            'body_html': '''<div style="margin: 0px; padding: 0px;">
				<p style="margin: 0px; padding: 0px; font-size: 13px;">
					Dear %s,<br/><br/>
					Your Payslip report from %s to %s
				</p>
				<p>

					<br/>
					Thank you.
				</p>
			</div>''' % ((self.employee_id.name), (self.date_from), (self.date_to)),
            'attachment_ids':[(6,0,[attachment_id.id])],
        })
        mail.sudo().send()
