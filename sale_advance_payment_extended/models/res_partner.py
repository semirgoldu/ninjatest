from odoo import fields, models


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    advance_amount = fields.Monetary(string='Remaining Partner Credit', currency_field='currency_id', copy=False, default=0.0, compute="get_total_partner_credit")
    account_payment_ids = fields.One2many("account.payment", "partner_id", string="Pay sale advanced", readonly=True)

    def get_total_partner_credit(self):
        for rec in self:
            account_types = []
            total_amount = []
            receivable_type = self.env.ref('account.data_account_type_receivable').id
            payable_type = self.env.ref('account.data_account_type_payable').id
            account_types.extend([receivable_type, payable_type])
            domain = [('partner_id', '=', rec.id), ('amount_residual', '!=', 0), ('amount_residual_currency', '!=', 0.0),
                      ('account_id.user_type_id', 'in', account_types), ('balance', '<', 0.0), ('move_id.state', '=', 'posted')]
            for line in self.env['account.move.line'].search(domain):
                amount = abs(line.amount_residual_currency)
                total_amount.append(amount)
            rec.advance_amount = sum(total_amount)
