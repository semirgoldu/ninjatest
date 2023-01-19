# See LICENSE file for full copyright and licensing details

from datetime import datetime
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import Warning


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'
    _description = 'Asset'

    sale_date = fields.Date(
        string='Sale Date',
        help='Sale Date of the Property.')
    sale_price = fields.Float(
        string='Sale Price',
        help='Sale price of the Property.')
    payment_term = fields.Many2one(
        comodel_name='account.payment.term',
        string='Payment Terms')
    sale_cost_ids = fields.One2many(
        comodel_name='sale.cost',
        inverse_name='property_id',
        string='Costs')
    customer_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer')
    end_date = fields.Date(
        string='End Date')
    purchase_price = fields.Float(
        string='Purchase Price',
        help='Purchase price of the Property.')
    multiple_owners = fields.Boolean(
        string='Multiple Owners',
        help="Check this box if there is multiple \
            Owner of the Property.")
    total_owners = fields.Integer(
        string='Number of Owners')
    recurring_rule_type = fields.Selection(
        [('monthly', 'Month(s)')],
        string='Recurrency',
        default='monthly',
        help="Invoice automatically repeat \
            at specified interval.")
    purchase_cost_ids = fields.One2many(
        comodel_name='cost.cost',
        inverse_name='property_id',
        string='Purchase Costs')
    note = fields.Text(
        string='Notes',
        help='Additional Notes.')
    return_period = fields.Float(
        compute='calc_return_period',
        string="Return Period(In Months)",
        store=True,
        help='Average of Purchase Price and Ground Rent.')

    
    @api.depends('purchase_price', 'ground_rent')
    def calc_return_period(self):
        """
        This Method is used to Calculate Return Period.
        ------------------------------------------------
        @param self: The object pointer
        @return: Calculated Return Period.
        """
        rtn_prd = 0
        for rtn in self:
            if rtn.ground_rent != 0 and rtn.purchase_price != 0:
                rtn_prd = rtn.purchase_price / rtn.ground_rent
            rtn.return_period = rtn_prd

    
    def create_purchase_installment(self):
        """
        This Button method is used to create purchase installment
        information entries.
        ----------------------------------------------------------
        @param self: The object pointer
        """
        year_create = []
        for res in self:
            amount = res['purchase_price']
            if amount == 0.0:
                raise Warning(_('Please Enter Valid Purchase Price'))
            if not res.end_date:
                raise Warning(_('Please Select End Date'))
            if res.end_date < res.date:
                raise Warning(
                    _("Please Select End Date greater than purchase date"))
    #        method used to calculate difference in month between two dates
            def diff_month(d1, d2):
                return (d1.year - d2.year) * 12 + d1.month - d2.month
            difference_month = diff_month(res.end_date, res.date)
            if difference_month == 0:
                amnt = amount
            else:
                if res.end_date.day > res.date.day:
                    difference_month += 1
                amnt = amount / difference_month
            # cr = self._cr
            self.env.cr.execute(
                "SELECT date FROM cost_cost WHERE property_id=%s" % res.id)
            exist_dates = self.env.cr.fetchall()
            date_add = self.date_addition(
                res.date, res.end_date, res.recurring_rule_type)
            exist_dates = map(lambda x: x[0], exist_dates)
            result = list(set(date_add) - set(exist_dates))
            result.sort(key=lambda item: item, reverse=False)
            ramnt = amnt
            remain_amnt = 0.0
            for dates in result:
                remain_amnt = amount - ramnt
                remain_amnt_per = (remain_amnt / amount) * 100
                if remain_amnt < 0:
                    remain_amnt = remain_amnt * -1
                if remain_amnt_per < 0:
                    remain_amnt_per = remain_amnt_per * -1
                year_create.append((0, 0, {
                    'currency_id': res.currency_id.id or False,
                    'date': dates,
                    'property_id': res.id,
                    'amount': amnt,
                    'remaining_amount': remain_amnt,
                    'rmn_amnt_per': remain_amnt_per,
                }))
                amount = remain_amnt
        return self.write({
            'purchase_cost_ids': year_create,
            'pur_instl_chck': True
        })

    
    def genrate_payment_enteries(self):
        """
        This Button method is used to generate property sale payment entries.
        ----------------------------------------------------------------------
        @param self: The object pointer
        """
        for data in self:
            amount = data.sale_price
            year_create = []
            pterm_list = [data.payment_term.compute(data.sale_price, data.sale_date)]
            if amount == 0.0:
                raise Warning(_('Please Enter Valid Sale Price'))
            rmnt = 0.0
            for line in pterm_list:
                lst = list(line[0])
                remain_amnt = amount - lst[1]
                remain_amnt_per = (remain_amnt / data.sale_price) * 100
                if remain_amnt < 0:
                    remain_amnt = remain_amnt * -1
                if remain_amnt_per < 0:
                    remain_amnt_per = remain_amnt_per * -1
                year_create.append((0, 0, {
                    'currency_id': data.currency_id.id or False,
                    'date': lst[0],
                    'property_id': data.id,
                    'amount': lst[1],
                    'remaining_amount': remain_amnt,''
                    'rmn_amnt_per': remain_amnt_per,
                }))
                amount = amount - lst[1]
            self.write({
                'sale_cost_ids': year_create,
                'sale_instl_chck': True
            })
        return True
