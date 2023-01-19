from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    is_account_approval = fields.Boolean("Get Account", default=True, copy=False)
    account_account_name = fields.Char("Account Name", default=True, copy=False)
    is_reversed_entry_done = fields.Boolean("Is Reversed Entries", copy=False)
    ref_document_number = fields.Char(copy=False, string="Reference Document No.")
    subject = fields.Char(copy=False)
    greeting_text = fields.Char(copy=False)
    analytic_tag_id = fields.Many2one("account.analytic.tag", "Analytical Tag")
    project_id = fields.Many2one("project.project", "Project")

    def apply_all_analytic_tag(self):
        for rec in self.invoice_line_ids:
            rec.analytic_tag_ids = self.analytic_tag_id

    def action_post(self):
        if any(self.line_ids.filtered(lambda x: not x.analytic_tag_ids)) and any(self.line_ids.filtered(lambda x: not x.analytic_account_id)):
            raise UserError("Please insert data in   Analytic Tags and Analytic Account.")
        elif any(self.line_ids.filtered(lambda x: not x.analytic_account_id)):
            raise UserError("Please insert data in  Analytic Account.")
        elif any(self.line_ids.filtered(lambda x: not x.analytic_tag_ids)):
            raise UserError("Please insert data in  Analytic Tags.")
        if self.is_account_approval == True and self.move_type == 'in_invoice':
            self.account_account_name = ', '.join(self.line_ids.mapped('account_id.name'))
            return self.approval_entries_account()
        else:
            return super(AccountMoveInherit, self).action_post()

    def approval_entries_account(self):
        return {
            'name': 'Account Approval',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('taqat_account_move_extended.account_journal_entries_approval_views').id,
            'res_model': 'account.journal.entries.approval',
            'domain': [],
            'context': {
                'move_id': self.id,
            },
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

class AccountReconciliationInherit(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'

    @api.model
    def _process_move_lines(self, move_line_ids, new_mv_line_dicts):
        """ Create new move lines from new_mv_line_dicts (if not empty) then call reconcile_partial on self and new move lines

            :param new_mv_line_dicts: list of dicts containing values suitable for account_move_line.create()
        """
        if len(move_line_ids) < 1 or len(move_line_ids) + len(new_mv_line_dicts) < 2:
            raise UserError(_('A reconciliation must involve at least 2 move lines.'))

        move_lines = self.env['account.move.line'].browse(move_line_ids)

        # Create writeoff move lines
        if len(new_mv_line_dicts) > 0:
            move_vals_list = [self._prepare_writeoff_moves(move_lines, vals) for vals in new_mv_line_dicts]
            if move_vals_list and move_vals_list[0] and move_vals_list[0].get('line_ids') and \
                    move_vals_list[0]['line_ids'][0][2].get('analytic_tag_ids'):
                for index_line in range(0, len(move_vals_list[0].get('line_ids'))):
                    if not move_vals_list[0]['line_ids'][index_line][2].get('analytic_tag_ids'):
                        move_vals_list[0]['line_ids'][index_line][2]['analytic_tag_ids'] = \
                        move_vals_list[0]['line_ids'][0][2]['analytic_tag_ids']
            if move_vals_list and move_vals_list[0] and move_vals_list[0].get('line_ids') and \
                    move_vals_list[0]['line_ids'][0][2].get('analytic_account_id'):
                for index_line in range(0, len(move_vals_list[0].get('line_ids'))):
                    if not move_vals_list[0]['line_ids'][index_line][2].get('analytic_account_id'):
                        move_vals_list[0]['line_ids'][index_line][2]['analytic_account_id'] = \
                        move_vals_list[0]['line_ids'][0][2]['analytic_account_id']
            moves = self.env['account.move'].create(move_vals_list)
            moves.action_post()
            account = move_lines[0].account_id
            move_lines |= moves.line_ids.filtered(lambda line: line.account_id == account and not line.reconciled)
        move_lines.reconcile()
