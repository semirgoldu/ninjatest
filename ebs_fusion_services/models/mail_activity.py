from odoo import api, fields, models


class MailActivityInherit(models.Model):
    _inherit = 'mail.activity'

    def action_close_dialog(self):
        res = super(MailActivityInherit, self).action_close_dialog()
        w_line = self.env['ebs.crm.proposal.workflow.line'].search([('id', '=', self.res_id)])
        if self.res_model_id.name == 'EBS Proposal Workflow Lines':
            if w_line.service_process_id:
                data = {
                    'activity_type_id': self.activity_type_id.id,
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'ebs.crm.service.process')]).id,
                    'res_id': w_line.service_process_id.id,
                    'note': self.note,
                    'summary': w_line.name+ ' '  + self.summary,
                    'user_id': self.user_id.id,
                }
                self.env['mail.activity'].create(data)
        return res
