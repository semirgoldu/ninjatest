from odoo import models, fields, api, _


class AccountAssetAssetInherit(models.Model):
    _inherit = 'account.asset.asset'

    building = fields.Char("Building")
    zone = fields.Char("Zone")
    electricity_no = fields.Char("Electricity No")
    water_no = fields.Char("Water No")
    free_rent = fields.Integer("Free Rent")
    furnished = fields.Selection(selection_add=[('unfirnsihed_with_AC', 'Unfirnsihed with AC')])
    location_code = fields.Char("Location Code")
    market_value = fields.Float(string="Market Value")
    budget_expense_ids = fields.One2many('budget.expense', 'property_id', 'Budget Expense')
    budget_revenue_ids = fields.One2many('budget.revenue', 'property_id', 'Budget Revenue')

    @api.onchange('parent_id')
    def parent_property_onchange(self):
        res = super(AccountAssetAssetInherit, self).parent_property_onchange()
        if self.parent_id:
            self.building = self.parent_id.building or ''
            self.zone = self.parent_id.zone or ''
            self.electricity_no = self.parent_id.electricity_no or ''
            self.water_no = self.parent_id.water_no or ''
            self.type_id = self.parent_id.type_id.id or ''
            self.property_manager = self.parent_id.property_manager or ''
            self.date = self.parent_id.date or ''
            self.is_compound = self.parent_id.is_compound or ''
            self.income_acc_id = self.parent_id.income_acc_id.id or ''
            self.expense_account_id = self.parent_id.expense_account_id.id or ''
            self.maint_account_id = self.parent_id.maint_account_id.id or ''
            self.company_id = self.parent_id.company_id.id or ''
            self.currency_id = self.parent_id.currency_id.id or ''
            self.account_analytic_id = self.parent_id.account_analytic_id.id or ''
            self.category_id = self.parent_id.category_id.id or ''

    def duplicate_property(self):
        action = self.env.ref('taqat_property_management.action_property_duplicate').read([])[0]
        action['context'] = {
            'active_id': self._context.get('active_id'),
        }
        return action


class BudgetExpense(models.Model):
    _name = "budget.expense"
    _description = 'Budget Expense'

    budget_year = fields.Char('Budget Year', required=True)
    amount = fields.Float('Amount')
    property_id = fields.Many2one('account.asset.asset')


class BudgetRevenue(models.Model):
    _name = "budget.revenue"
    _description = 'Budget Revenue'

    budget_year = fields.Char('Budget Year', required=True)
    amount = fields.Float('Amount')
    property_id = fields.Many2one('account.asset.asset')
