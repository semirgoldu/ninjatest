import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountAnalyticAccountInherit(models.Model):
    _name = 'account.analytic.account'
    _inherit = ['account.analytic.account', 'mail.thread', 'mail.activity.mixin']

    location_code = fields.Char("Location Code")
    is_tenant_tenancy = fields.Boolean("Is Tenant Tenancy")
    mobile = fields.Char(related='tenant_id.mobile', store=True)
    reference_no = fields.Char("Reference No.")
    acknowledgment_no = fields.Char("Acknowledgment No")
    lease_type = fields.Selection(
        [('lease', 'Leased'), ('maintenance', 'Maintenance'), ('renewal', 'Renewal'), ('new_contract', 'New Contract')],
        'Lease Type')
    cheque_detail = fields.Char("Cheques Number")
    maturity_date_line = fields.Date("Maturity Date")
    bank_name = fields.Char("Bank Name")
    old_tenancy_contract = fields.Many2one("account.analytic.account", "Old Tenancy Contract",
                                           domain=[('is_tenant_tenancy', '=', True)])
    free_months = fields.Integer(string='Free Months')
    active_free_rent = fields.Boolean(string='Active Free Rent')
    free_from = fields.Date(string='Free From')
    free_to = fields.Date(string='Free To')
    frequency = fields.Selection([('monthly', 'Monthly'), ('yearly', 'Yearly')], 'Frequency')

    @api.depends('line_ids')
    def _compute_purchase_order_count(self):
        for account in self:
            account.purchase_order_count = self.env['purchase.order'].sudo().search_count([
                ('order_line.invoice_lines.analytic_line_ids.account_id', '=', account.id)
            ])

    def check_expiration_properties(self):
        properties = self.search([])
        today = datetime.datetime.today().date()
        date_after_two_month = today + relativedelta(months=+2)
        properties = properties.filtered(lambda x:x.date and x.date == date_after_two_month)
        for rec in properties:
            users = []
            activity_type_id = self.env.ref('taqat_property_management.mail_act_properties_expiration')
            activity_obj = self.env['mail.activity']
            users += self.env.ref('taqat_groups_access_rights_extended.taqat_group_property_employee_role').users
            for user in users:
                vals = {
                    'activity_type_id': activity_type_id.id,
                    'note': "Kindly check this Property Expire on %s." %(rec.date),
                    'user_id': user.id,
                    'res_id': rec.id,
                    'res_model': 'account.analytic.account',
                    'res_model_id': self.env['ir.model'].sudo()._get('account.analytic.account').id,
                }
                activity_obj.sudo().create(vals)

    def button_set_to_renew(self):
        vals = {
            'name': self.name,
            'property_id': self.property_id.id if self.property_id else False,
                'tenant_id': self.tenant_id.id if self.tenant_id else False,
                'location_code': self.location_code,
                'old_tenancy_contract': self.id,
                'reference_no': self.reference_no,
                'lease_type': 'renewal',
                'multi_prop': self.multi_prop,
                'manager_id': self.manager_id.id if self.manager_id else False,
                'mobile': self.mobile,
                'is_tenant_tenancy': self.is_tenant_tenancy,
                'currency_id': self.currency_id.id,
                'rent': self.rent,
                'ten_date': datetime.datetime.today().date(),
                'deposit': self.deposit,
                'deposit_received': self.deposit_received,
                'amount_return': self.amount_return,
                'deposit_return': self.deposit_return,
                'main_cost': self.main_cost,
                'contact_id': self.contact_id.id if self.contact_id else False,
                'date_start': self.date_start,
                'date': self.date,
                'total_rent': self.total_rent,
                'rent_type_id': self.rent_type_id.id if self.rent_type_id else False,
                'commission': self.commission,
                'penalty': self.penalty,
                'penalty_day': self.penalty_day,
                'agent': self.agent.id if self.agent else False,
                'commission_type': self.commission_type,
                'total_commission': self.total_commission}
        new_renewal_tenancy_tenant = self.env['account.analytic.account'].create(vals)
        action = self.env.ref('property_management.action_property_analytic_view').sudo().read()[0]
        res_id = new_renewal_tenancy_tenant.id
        action['views'] = [(self.env.ref('property_management.property_analytic_view_form').id, 'form')]
        action['view_mode'] = 'form'
        action['res_id'] = res_id
        action['target'] = 'current'
        return action

    def set_detail(self):
        if self.rent_schedule_ids and self.date_start:
            cheque_detail = self.cheque_detail
            for rec in self.rent_schedule_ids:
                rec.cheque_detail = cheque_detail
                cheque_detail = str(self.increment(cheque_detail))

    def increment(self, s):
        import re
        try:
            a, b = re.match('(\D*)(\d+)', s).groups()
        except (AttributeError, IndexError):
            return
        return f'{a}{int(b) + 1:0{len(b)}d}'

    def set_maturity_date(self):
        if self.maturity_date_line:
            if self.rent_schedule_ids and self.date_start:
                maturity_date_line = self.maturity_date_line
                for rec in self.rent_schedule_ids:
                    rec.maturity_date = maturity_date_line
                    maturity_date_line = maturity_date_line + relativedelta(months=1)
        else:
            raise ValidationError('Please Enter Maturity Date')

    def set_bank_name(self):
        if self.bank_name:
            if self.rent_schedule_ids:
                bank = self.bank_name
                for rec in self.rent_schedule_ids:
                    rec.bank_name = bank
        else:
            raise ValidationError('Please Enter Bank Name.')

    def create_rent_schedule(self):
        """
        This button method is used to create rent schedule Lines.
        @param self: The object pointer
        """
        rent_obj = self.env['tenancy.rent.schedule']
        for tenancy_rec in self:
            if tenancy_rec.rent_type_id.renttype == 'Weekly':
                d1 = tenancy_rec.date_start
                d2 = tenancy_rec.date
                interval = int(tenancy_rec.rent_type_id.name)
                if d2 < d1:
                    raise Warning(
                        _('End date must be greater than start date.'))
                wek_diff = (d2 - d1)
                wek_tot1 = (wek_diff.days) / (interval * 7)
                wek_tot = (wek_diff.days) % (interval * 7)
                if wek_diff.days == 0:
                    wek_tot = 1
                if wek_tot1 > 0:
                    for wek_rec in range(int(wek_tot1)):
                        rent_obj.create(
                            {'start_date': d1,
                             'amount': tenancy_rec.rent * interval or 0.0,
                             'community_amount': tenancy_rec.community * interval or 0.0,
                             'property_id': tenancy_rec.property_id
                                            and tenancy_rec.property_id.id or False,
                             'tenancy_id': tenancy_rec.id,
                             'currency_id': tenancy_rec.currency_id.id
                                            or False,
                             'rel_tenant_id': tenancy_rec.tenant_id.id
                             })
                        d1 = d1 + relativedelta(days=(7 * interval))
                if wek_tot > 0:
                    one_day_rent = 0.0
                    one_day_com_rent = 0.0
                    if tenancy_rec.rent:
                        one_day_rent = (tenancy_rec.rent) / (7 * interval)
                    if tenancy_rec.community_amount:
                        one_day_com_rent = (tenancy_rec.community) / (7 * interval)
                    rent_obj.create(
                        {'start_date': d1.strftime(
                            DEFAULT_SERVER_DATE_FORMAT),
                            'end_date': d1.strftime(
                                DEFAULT_SERVER_DATE_FORMAT),
                            'amount': (one_day_rent * (wek_tot)) or 0.0,
                            'community_amount': (one_day_com_rent * (wek_tot)) or 0.0,
                            'property_id': tenancy_rec.property_id
                                           and tenancy_rec.property_id.id or False,
                            'tenancy_id': tenancy_rec.id,
                            'currency_id': tenancy_rec.currency_id.id or False,
                            'rel_tenant_id': tenancy_rec.tenant_id.id
                        })
            elif tenancy_rec.rent_type_id.renttype != 'Weekly':
                if tenancy_rec.rent_type_id.renttype == 'Monthly':
                    interval = int(tenancy_rec.rent_type_id.name)
                if tenancy_rec.rent_type_id.renttype == 'Yearly':
                    interval = int(tenancy_rec.rent_type_id.name) * 12
                d1 = tenancy_rec.date_start
                d2 = tenancy_rec.date
                diff = abs((d1.year - d2.year) * 12 + (d1.month - d2.month))
                tot_rec = diff / interval
                tot_rec2 = diff % interval
                if abs(d1.month - d2.month) >= 0 and d1.day < d2.day:
                    tot_rec2 += 1
                if diff == 0:
                    tot_rec2 = 1
                if tot_rec > 0:
                    for rec in range(int(tot_rec)):
                        rent_obj.create(
                            {'start_date': d1,
                             'end_date': d1 + relativedelta(days=-1, months=1),
                             'amount': tenancy_rec.rent * interval or 0.0,
                             'community_amount': tenancy_rec.community * interval or 0.0,
                             'property_id': tenancy_rec.property_id
                                            and tenancy_rec.property_id.id or False,
                             'tenancy_id': tenancy_rec.id,
                             'currency_id': tenancy_rec.currency_id.id
                                            or False,
                             'rel_tenant_id': tenancy_rec.tenant_id.id
                             })
                        d1 = d1 + relativedelta(months=interval)
                if tot_rec2 > 0:
                    rent_obj.create({
                        'start_date': d1,
                        'end_date': d1 + relativedelta(days=-1, months=1),
                        'amount': tenancy_rec.rent * tot_rec2 or 0.0,
                        'community_amount': tenancy_rec.community * tot_rec2 or 0.0,
                        'property_id': tenancy_rec.property_id
                                       and tenancy_rec.property_id.id or False,
                        'tenancy_id': tenancy_rec.id,
                        'currency_id': tenancy_rec.currency_id.id or False,
                        'rel_tenant_id': tenancy_rec.tenant_id.id
                    })
            return tenancy_rec.write({'rent_entry_chck': True})

    def contract_send_by_mail(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env['ir.model.data']._xmlid_to_res_id('taqat_property_management.mail_template_tenancy_contract',raise_if_not_found=False)
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'account.analytic.account',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            # 'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
