from odoo import models, fields, api, _


class ProjectInherit(models.Model):
    _inherit = 'project.project'

    budget_position_id = fields.One2many('budget.position.project', 'project_id')


class BudgetaryPosition(models.Model):
    _name = 'budget.position.project'
    _description = 'Budget Position Project'

    project_id = fields.Many2one('project.project')
    position_id = fields.Many2one('account.budget.post', string="Budgetary Position", required=True)
    description = fields.Char(string="Description")
    amount = fields.Float(string="Amount")
    spent_amount = fields.Float(string="Spent Amount", readonly=True)
