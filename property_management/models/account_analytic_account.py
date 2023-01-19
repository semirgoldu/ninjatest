# See LICENSE file for full copyright and licensing details

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"
    _order = 'code'

    
    @api.depends('account_move_line_ids')
    def _compute_total_deb_cre_amt(self):
        """
        This method is used to calculate Total income amount.
        @param self: The object pointer
        """
        for tenancy_brw in self:
            total = tenancy_brw.total_credit_amt - tenancy_brw.total_debit_amt
            tenancy_brw.total_deb_cre_amt = total or 0.0

    
    @api.depends('account_move_line_ids')
    def _compute_total_credit_amt(self):
        """
        This method is used to calculate Total credit amount.
        @param self: The object pointer
        """
        for tenancy_brw in self:
            tenancy_brw.total_credit_amt = sum(
                credit_amt.credit for credit_amt in
                tenancy_brw.account_move_line_ids)

    
    @api.depends('account_move_line_ids')
    def _compute_total_debit_amt(self):
        """
        This method is used to calculate Total debit amount.
        @param self: The object pointer
        """
        for tenancy_brw in self:
            tenancy_brw.total_debit_amt = sum(
                debit_amt.debit for debit_amt in
                tenancy_brw.account_move_line_ids)

    
    @api.depends('rent_schedule_ids', 'rent_schedule_ids.amount')
    def _compute_total_rent(self):
        """
        This method is used to calculate Total Rent of current Tenancy.
        @param self: The object pointer
        @return: Calculated Total Rent.
        """
        for tenancy_brw in self:
            tenancy_brw.total_rent = sum(
                propety_brw.amount for propety_brw in
                tenancy_brw.rent_schedule_ids)

    @api.depends('property_id')
    def _compute_compound(self):
        for tenancy_brw in self:
            def check_compound(property_id):
                if property_id.is_compound:
                    tenancy_brw.is_compound = True
                else:
                    if property_id.parent_id:
                        check_compound(property_id.parent_id)
                    else:
                        tenancy_brw.is_compound = False
            check_compound(tenancy_brw.property_id)


    @api.depends('deposit')
    def _compute_payment_type(self):
        """
        This method is used to set deposit return and deposit received
        boolean field accordingly to current Tenancy.
        @param self: The object pointer
        """
        for tennancy in self:
            payments = self.env['account.payment'].search(
                    [('tenancy_id', '=', tennancy.id),
                     ('state', '=', 'posted'),('payment_type','=','inbound')])
            tennancy.deposit_received = len(payments.ids) and True or False

    # @api.depends('property_id')
    # def _get_property(self):
    #     main_list = []
    #     for ten in self:
    #         if ten.property_id.child_ids:
    #             print("ten.property_id.child_ids>>>>>>>>>>>>>>", ten.property_id.child_ids)
    #             for parent_grp in ten.property_id.child_ids:
    #                 main_list.append(parent_grp.id)
    #                 if parent_grp.child_ids:
    #                     parent_ids = self.get_parent_groups(parent_grp.id)
    #                     for parent_id in parent_ids:
    #                         main_list.append(parent_id)
    #         print("main_list>>>>>>>>>>>>>>",main_list)
    #     if main_list:
    #         return True
    #     else:
    #         return False

    contract_attachment = fields.Binary(
        string='Tenancy Contract',
        help='Contract document attachment for selected property')
    is_property = fields.Boolean(
        string='Is Property?')
    rent_entry_chck = fields.Boolean(
        string='Rent Entries Check',
        default=False)
    deposit_received = fields.Boolean(
        string='Deposit Received?',
        default=False,

        compute='_compute_payment_type',
        help="True if deposit amount received for current Tenancy.")
    deposit_return = fields.Boolean(
        string='Deposit Returned?',
        default=False,

        type='boolean',
        compute='amount_return_compute',
        help="True if deposit amount returned for current Tenancy.")
    code = fields.Char(
        string='Reference',
        default="/")
    doc_name = fields.Char(
        string='Filename')
    date = fields.Date(
        string='Expiration Date',
        index=True,
        help="Tenancy contract end date.")
    date_start = fields.Date(
        string='Start Date',
        default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),
        help="Tenancy contract start date .")
    ten_date = fields.Date(
        string='Date',
        default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),
        index=True,
        help="Tenancy contract creation date.")
    amount_fee_paid = fields.Integer(
        string='Amount of Fee Paid')
    manager_id = fields.Many2one(
        comodel_name='res.users',
        string='Account Manager',
        help="Manager of Tenancy.")
    property_id = fields.Many2one(
        comodel_name='account.asset.asset',
        string='Property',
        copy=False,
        help="Name of Property.")
    tenant_id = fields.Many2one(
        comodel_name='tenant.partner',
        string='Tenant',
        domain="[('tenant', '=', True)]",
        help="Tenant Name of Tenancy.")
    contact_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
        help="Contact person name.")
    rent_schedule_ids = fields.One2many(
        comodel_name='tenancy.rent.schedule',
        inverse_name='tenancy_id',
        string='Rent Schedule')
    account_move_line_ids = fields.One2many(
        comodel_name='account.move.line',
        inverse_name='analytic_account_id',
        string='Entries',
        readonly=True,
        states={'draft': [('readonly', False)]})
    is_compound = fields.Boolean(string="Compound", compute='_compute_compound')
    community = fields.Monetary(
        string='Community Fee',
        default=0.0,
        currency_field='currency_id',
        help="Community Fee")
    rent = fields.Monetary(
        string='Tenancy Rent',
        default=0.0,
        currency_field='currency_id',
        help="Tenancy rent for selected property per Month.")
    deposit = fields.Monetary(
        string='Deposit',
        default=0.0,
        currency_field='currency_id',
        help="Deposit amount for tenancy.")
    total_rent = fields.Monetary(
        string='Total Rent',
        store=True,
        readonly=True,
        currency_field='currency_id',
        compute='_compute_total_rent',
        help='Total rent of this Tenancy.')
    amount_return = fields.Monetary(
        string='Deposit Returned',
        default=0.0,
        currency_field='currency_id',
        help="Deposit Returned amount for Tenancy.")
    total_debit_amt = fields.Monetary(
        string='Total Debit Amount',
        default=0.0,
        compute='_compute_total_debit_amt',
        currency_field='currency_id')
    total_credit_amt = fields.Monetary(
        string='Total Credit Amount',
        default=0.0,
        compute='_compute_total_credit_amt',
        currency_field='currency_id')
    total_deb_cre_amt = fields.Monetary(
        string='Total Expenditure',
        default=0.0,
        compute='_compute_total_deb_cre_amt',
        currency_field='currency_id')
    description = fields.Text(
        string='Description',
        help='Additional Terms and Conditions')
    duration_cover = fields.Text(
        string='Duration of Cover',
        help='Additional Notes')
    acc_pay_dep_rec_id = fields.Many2one(
        comodel_name='account.payment',
        string='Account Payment',
        help="Manager of Tenancy.")
    acc_pay_dep_ret_id = fields.Many2one(
        comodel_name='account.payment',
        string='Tenancy Manager',
        help="Manager of Tenancy.")
    rent_type_id = fields.Many2one(
        comodel_name='rent.type',
        string='Rent Type')
    deposit_scheme_type = fields.Selection(
        [('insurance', 'Insurance-based')],
        'Type of Scheme')
    state = fields.Selection(
        [('template', 'Template'),
         ('draft', 'New'),
         ('open', 'In Progress'), ('pending', 'To Renew'),
         ('close', 'Closed'), ('cancelled', 'Cancelled')],
        string='Status',
        required=True,
        copy=False,
        default='draft')
    invc_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice')
    multi_prop = fields.Boolean(
        string='Multiple Property',
        help="Check this box Multiple property.")
    penalty_a = fields.Boolean(
        'Penalty')
    recurring = fields.Boolean(
        'Recurring')
    main_cost = fields.Float(
        string='Maintenance Cost',
        default=0.0,
        help="Insert maintenance cost")
    tenancy_cancelled = fields.Boolean(
        string='Tanency Cancelled',
        default=False)

    @api.constrains('date_start', 'date')
    def check_date_overlap(self):
        """
        This is a constraint method used to check the from date smaller than
        the Exiration date.
        @param self : object pointer
        """
        for rec in self:
            if rec.date_start and rec.date:
                if rec.date < rec.date_start:
                    raise ValidationError(
                        _('Expiration date should be grater then Start Date!'))

    @api.constrains('rent')
    def check_rent_positive(self):
        """
        This is a constraint method used to check the from date smaller than
        the Exiration date.
        @param self : object pointer
        """
        for rec in self:
            if rec.rent < 0 :
                raise ValidationError(
                    _('Rent amount should be strickly positive.'))

    @api.model
    def create(self, vals):
        """
        This Method is used to overrides orm create method,
        to change state and tenant of related property.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if 'tenant_id' in vals:
            vals['code'] = self.env['ir.sequence'].next_by_code(
                'account.analytic.account')
            vals.update({'is_property': True})
        if 'property_id' in vals:
            prop_brw = self.env['account.asset.asset'].browse(
                vals['property_id'])
            if vals.get('is_property') == True:
                prop_brw.write(
                    {'current_tenant_id': vals.get('tenant_id', False),
                     'state': 'book'})
        return super(AccountAnalyticAccount, self).create(vals)

    
    def write(self, vals):
        """
        This Method is used to overrides orm write method,
        to change state and tenant of related property.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        rec = super(AccountAnalyticAccount, self).write(vals)
        for tenancy_rec in self:
            if tenancy_rec.is_property== True:
                if vals.get('state'):
                    if vals['state'] == 'open':
                        tenancy_rec.property_id.write({
                            'current_tenant_id': tenancy_rec.tenant_id.id,
                            'state': 'normal'})
                    if vals['state'] == 'close':
                        tenancy_rec.property_id.write(
                            {'state': 'draft', 'current_tenant_id': False})
        return rec

    
    def unlink(self):
        """
        Overrides orm unlink method,
        @param self: The object pointer
        @return: True/False.
        """
        analytic_line_obj = self.env['account.analytic.line']
        rent_schedule_obj = self.env['tenancy.rent.schedule']
        for tenancy_rec in self:
            analytic_line_rec = analytic_line_obj.search(
                [('account_id', '=', tenancy_rec.id)])
            if analytic_line_rec and analytic_line_rec.ids:
                analytic_line_rec.unlink()
            rent_ids = rent_schedule_obj.search(
                [('tenancy_id', '=', tenancy_rec.id)])
            if any(rent.move_check for rent in rent_ids):
                raise Warning(
                    _('You cannot delete Tenancy record, if any related Rent \
                    Schedule entries are in posted.'))
            else:
                rent_ids.unlink()
            if tenancy_rec.property_id.property_manager and \
                    tenancy_rec.property_id.property_manager.id:
                releted_user = tenancy_rec.property_id.property_manager.id
                new_ids = self.env['res.users'].search(
                    [('partner_id', '=', releted_user)])
                if releted_user and new_ids and new_ids.ids:
                    new_ids.write(
                        {'tenant_ids': [(3, tenancy_rec.tenant_id.id)]})
            tenancy_rec.property_id.write(
                {'state': 'draft', 'current_tenant_id': False})
        return super(AccountAnalyticAccount, self).unlink()

    
    @api.depends('amount_return')
    def amount_return_compute(self):
        """
        When you change Deposit field value, this method will change
        amount_fee_paid field value accordingly.
        @param self: The object pointer
        """
        for data in self:
            data.deposit_return = data.amount_return > 0.00 and True or False

    @api.onchange('property_id')
    def onchange_property_id(self):
        """
        This Method is used to set property related fields value,
        on change of property.
        @param self: The object pointer
        """
        search_domain = []
        if self.property_id:
            self.rent = self.property_id.ground_rent or False
            self.rent_type_id = self.property_id.rent_type_id and \
                self.property_id.rent_type_id.id or False


    
    def button_receive(self):
        """
        This button method is used to open the related
        account payment form view.
        @param self: The object pointer
        @return: Dictionary of values.
        """
        payment_id = False
        acc_pay_form = self.env.ref(
            'account.view_account_payment_form')
        account_jrnl_obj = self.env['account.journal'].search(
            [('type', '=', 'purchase')], limit=1)
        payment_obj = self.env['account.payment']
        payment_method_id = self.env.ref(
            'account.account_payment_method_manual_in')
        for tenancy_rec in self:
            if tenancy_rec.acc_pay_dep_rec_id and \
                    tenancy_rec.acc_pay_dep_rec_id.id:
                return {
                    # 'view_type': 'form',
                    'view_id': acc_pay_form.id,
                    'view_mode': 'form',
                    'res_model': 'account.payment',
                    'res_id': tenancy_rec.acc_pay_dep_rec_id.id,
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'context': self._context,
                }
            if tenancy_rec.deposit == 0.00:
                raise Warning(_('Please Enter Deposit amount.'))
            if tenancy_rec.deposit < 0.00:
                raise Warning(
                    _('The deposit amount must be strictly positive.'))
            vals = {
                'partner_id': tenancy_rec.tenant_id.parent_id.id,
                'partner_type': 'customer',
                'journal_id': account_jrnl_obj.id,
                'payment_type': 'inbound',
                'ref': 'Deposit Received',
                'tenancy_id': tenancy_rec.id,
                'amount': tenancy_rec.deposit,
                'property_id': tenancy_rec.property_id.id,
                'payment_method_id': payment_method_id.id
            }
            payment_id = payment_obj.create(vals)
        return {
                'view_mode': 'form',
                'view_id': acc_pay_form.id,
                # 'view_type': 'form',
                'res_id': payment_id and payment_id.id,
                'res_model': 'account.payment',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'domain': '[]',
                'context': {
                    'close_after_process': True,
                }
            }

    
    def button_return(self):
        """
        This method create supplier invoice for returning deposite
        amount.
        -----------------------------------------------------------
        @param self: The object pointer
        """
        account_jrnl_obj = self.env['account.journal'].search(
            [('type', '=', 'purchase')], limit=1)
        invoice_obj = self.env['account.move']
        wiz_form_id = self.env.ref('account.invoice_supplier_form').id
        for rec in self:
            inv_line_values = {
                'name': _('Deposit Return') or "",
                'origin': 'account.analytic.account' or "",
                'quantity': 1,
                'account_id': rec.property_id.expense_account_id.id or False,
                'price_unit': rec.deposit or 0.00,
                'account_analytic_id': rec.id or False,
            }
            if rec.multi_prop:
                for data in rec.prop_id:
                    for account in data.property_ids.income_acc_id:
                        account_id = account.id
                    inv_line_values.update({'account_id': account_id})

            inv_values = {
                'origin': _('Deposit Return For ') + rec.name or "",
                'type': 'in_invoice',
                'property_id': rec.property_id.id,
                'partner_id': rec.tenant_id.parent_id.id or False,
                'account_id':
                    rec.tenant_id.parent_id.property_account_payable_id.id
                        or False,
                'invoice_line_ids': [(0, 0, inv_line_values)],
                'date_invoice': datetime.now().strftime(
                    DEFAULT_SERVER_DATE_FORMAT) or False,
                'new_tenancy_id': rec.id,
                'reference': rec.code,
                'journal_id':
                account_jrnl_obj and account_jrnl_obj.id or False,
            }
            acc_id = invoice_obj.create(inv_values)
            rec.write({'invc_id': acc_id.id})
        return {
                # 'view_type': 'form',
                'view_id': wiz_form_id,
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': self.invc_id.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': rec._context,
            }

    
    def button_start(self):
        """
        This button method is used to Change Tenancy state to Open.
        @param self: The object pointer
        """
        user_obj = self.env['res.users']
        for current_rec in self:
            if current_rec.property_id.property_manager and \
                    current_rec.property_id.property_manager.id:
                releted_user = current_rec.property_id.property_manager.id
                new_ids = user_obj.search(
                    [('partner_id', '=', releted_user)])
                if releted_user and new_ids and new_ids.ids:
                    new_ids.write(
                        {'tenant_ids': [(4, current_rec.tenant_id.id)]})
        return self.write({'state': 'open', 'rent_entry_chck': False})

    
    def button_close(self):
        """
        This button method is used to Change Tenancy state to close.
        @param self: The object pointer
        """
        for rec in self:
            rec.write({'state': 'close'})

    
    def button_set_to_draft(self):
        """
        This button method is used to Change Tenancy state to close.
        @param self: The object pointer
        """
        for rec in self:
            rec.write({
                'state': 'draft',
                'rent_schedule_ids': [(2, rec.rent_schedule_ids.ids)]})

    
    def button_set_to_renew(self):
        """
        This Method is used to open Tenancy renew wizard.
        @param self: The object pointer
        @return: Dictionary of values.
        """
        self.ensure_one()
        rent_schedule_obj = self.env['tenancy.rent.schedule']
        for tenancy_brw in self:
            if rent_schedule_obj.search(
                [('tenancy_id', '=', tenancy_brw.id),
                 ('move_check', '=', False)]):
                raise ValidationError(
                    _('In order to Renew a Tenancy, Please make all related Rent Schedule entries posted.'))
        return {
            'name': _('Tenancy Renew Wizard'),
            'res_model': 'renew.tenancy',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            # 'view_type': 'form',
            'target': 'new',
            'context': {'default_start_date': self.date}
        }

    @api.model
    def cron_property_states_changed(self):
        """
        This Method is called by Scheduler for change property state
        according to tenancy state.
        @param self: The object pointer
        """
        curr_date = datetime.now().date()
        tncy_rec = self.search([('date_start', '<=', curr_date),
                                ('date', '>=', curr_date),
                                ('state', '=', 'open'),
                                ('is_property', '=', True)])
        for tncy_data in tncy_rec:
            if tncy_data.property_id and tncy_data.property_id.id:
                tncy_data.property_id.write(
                    {'state': 'normal', 'color': 7})
        return True

    @api.model
    def cron_property_tenancy(self):
        """
        This Method is called by Scheduler to send email
        to tenant as a reminder for rent payment.
        @param self: The object pointer
        """
        due_date = datetime.now().date() + relativedelta(days=7)
        tncy_ids = self.search(
            [('is_property', '=', True), ('state', '=', 'open')])
        rent_schedule_obj = self.env['tenancy.rent.schedule']
        model_data_id = self.env.ref(
            'property_management.property_email_template')
        for tncy_data in tncy_ids:
            tncy_rent_ids = rent_schedule_obj.search(
                [('tenancy_id', '=', tncy_data.id),
                 ('start_date', '=', due_date)])
            for tenancy in tncy_rent_ids:
                model_data_id.send_mail(
                    tenancy.id, force_send=True, raise_exception=False)
        return True

    
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
                             'community_amount':tenancy_rec.community * interval or 0.0,
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
                        'amount': tenancy_rec.rent * tot_rec2 or 0.0,
                        'community_amount': tenancy_rec.community * tot_rec2 or 0.0,
                        'property_id': tenancy_rec.property_id
                        and tenancy_rec.property_id.id or False,
                        'tenancy_id': tenancy_rec.id,
                        'currency_id': tenancy_rec.currency_id.id or False,
                        'rel_tenant_id': tenancy_rec.tenant_id.id
                    })
            return tenancy_rec.write({'rent_entry_chck': True})

    
    def button_cancel_tenancy(self):
        """
        This button method is used to Change Tenancy state to Cancelled.
        @param self: The object pointer
        """
        for record in self:
            record.write(
                {'state': 'cancelled', 'tenancy_cancelled': True})
            record.property_id.write(
                {'state': 'draft'})
            rent_ids = self.env['tenancy.rent.schedule'].search(
                [('tenancy_id', '=', record.id),
                 ('paid', '=', False),
                 ('move_check', '=', False)])
            for value in rent_ids:
                value.write({'is_readonly': True})
        return True
