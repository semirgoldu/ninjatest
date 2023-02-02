from odoo import models, fields, api, _


class ProjectInherit(models.Model):
    _inherit = 'project.project'

    budget_position_id = fields.One2many('budget.position.project', 'project_id')
    total_project_purchase_invoiced = fields.Monetary(compute='vendor_invoice_total', string="Total Vendor Invoiced",
        groups='account.group_account_invoice,account.group_account_readonly')
    total_project_sale_invoiced = fields.Monetary(compute='customer_invoice_total', string="Total Vendor Invoiced",
                                                      groups='account.group_account_invoice,account.group_account_readonly')

    def vendor_invoice_total(self):
        self.total_project_purchase_invoiced = 0
        if not self.ids:
            return True

        domain = [
            ('project_id', "=", int(self.filtered('id'))),
            ('state', 'not in', ['draft', 'cancel']),
            ('move_type', 'in', ('in_invoice', 'in_refund')),
        ]
        price_totals = self.env['account.invoice.report'].read_group(domain, ['price_subtotal'],['project_id'])
        self.total_project_purchase_invoiced = sum(price['price_subtotal'] for price in price_totals)

    def customer_invoice_total(self):
        self.total_project_sale_invoiced = 0
        if not self.ids:
            return True

        domain = [
            ('project_id', "=", int(self.filtered('id'))),
            ('state', 'not in', ['draft', 'cancel']),
            ('move_type', 'in', ('out_invoice', 'out_refund')),
        ]
        price_totals = self.env['account.invoice.report'].read_group(domain, ['price_subtotal'],['project_id'])
        self.total_project_sale_invoiced = sum(price['price_subtotal'] for price in price_totals)
    def action_view_project_purchase_invoices(self):
        return {

            'name': ('Vendor Bills'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': [('project_id', '=', self.id),('move_type', 'in', ('in_invoice', 'in_refund'))]
        }

    def action_view_project_sale_invoices(self):
        return {

            'name': ('Customer Invoices'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': [('project_id', '=', self.id),('move_type', 'in', ('out_invoice', 'out_refund'))]
        }


class BudgetaryPosition(models.Model):
    _name = 'budget.position.project'
    _description = 'Budget Position Project'

    project_id = fields.Many2one('project.project')
    position_id = fields.Many2one('account.budget.post', string="Budgetary Position", required=True)
    description = fields.Char(string="Description")
    amount = fields.Float(string="Amount")
    spent_amount = fields.Float(string="Spent Amount", readonly=True)
