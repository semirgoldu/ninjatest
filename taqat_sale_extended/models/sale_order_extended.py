from odoo import models, fields, api, _


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    subject = fields.Char('Subject')
    valid_days = fields.Float("Valid for (Days)")
    crm_count = fields.Integer('CRM Lead', compute='_compute_crm_lead_count')


    def _compute_crm_lead_count(self):
        Crm = self.env['crm.lead']
        for rec in self:
            rec.crm_count = Crm.search_count([('id', '=', self.opportunity_id.id)]) or 0

    def get_sale_crm(self):
        action = self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_action_pipeline")
        tree_view = [(self.env.ref('crm.crm_case_tree_view_oppor').id, 'tree')]
        action['views'] = tree_view + [(state, view) for state, view in action['views'] if view != 'tree']

        action['domain'] = [('id', '=', self.opportunity_id.id)]
        action['context'] = {}
        return action
