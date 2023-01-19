from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, AccessError


class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    visa_number = fields.Char(string='Visa Number', help='Visa Number of the customer.')

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrderInherit, self)._order_fields(ui_order)
        res['visa_number'] = ui_order.get('visa_number', '')
        return res

    # def _apply_invoice_payments(self):
    #     receivable_account = self.env["res.partner"]._find_accounting_partner(self.partner_id).property_account_receivable_id
    #     payment_moves = self.payment_ids._create_payment_moves()
    #     analytic_account_id = self.config_id.analytic_account_id.id if self.config_id and self.config_id.analytic_account_id else False
    #     analytic_tag_ids = [(6, 0, self.config_id.analytic_tag_ids.ids)] if self.config_id and self.config_id.analytic_tag_ids else [(6, 0, [])]
    #     for move in payment_moves:
    #         for line in move.line_ids:
    #             line.sudo().write({
    #                 'analytic_account_id': analytic_account_id,
    #                 'analytic_tag_ids': analytic_tag_ids,
    #             })
    #     invoice_receivable = self.account_move.line_ids.filtered(lambda line: line.account_id == receivable_account)
    #     # Reconcile the invoice to the created payment moves.
    #     # But not when the invoice's total amount is zero because it's already reconciled.
    #     if not invoice_receivable.reconciled and receivable_account.reconcile:
    #         payment_receivables = payment_moves.mapped('line_ids').filtered(lambda line: line.account_id == receivable_account)
    #         (invoice_receivable | payment_receivables).reconcile()

    # def _generate_pos_order_invoice(self):
    #     moves = self.env['account.move']
    #
    #     for order in self:
    #         # Force company for all SUPERUSER_ID action
    #         if order.account_move:
    #             moves += order.account_move
    #             continue
    #
    #         if not order.partner_id:
    #             raise UserError(_('Please provide a partner for the sale.'))
    #
    #         move_vals = order._prepare_invoice_vals()
    #         new_move = order._create_invoice(move_vals)
    #
    #         analytic_account_id = order.config_id.analytic_account_id.id if order.config_id and order.config_id.analytic_account_id else False
    #         analytic_tag_ids = [(6, 0, order.config_id.analytic_tag_ids.ids)] if order.config_id and order.config_id.analytic_tag_ids else [(6, 0, [])]
    #         for line in new_move.line_ids:
    #             line.sudo().write({
    #                 'analytic_account_id': analytic_account_id,
    #                 'analytic_tag_ids': analytic_tag_ids,
    #             })
    #         order.write({'account_move': new_move.id, 'state': 'invoiced'})
    #         new_move.sudo().with_company(order.company_id)._post()
    #         moves += new_move
    #         order._apply_invoice_payments()
    #
    #     if not moves:
    #         return {}
    #
    #     return {
    #         'name': _('Customer Invoice'),
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('account.view_move_form').id,
    #         'res_model': 'account.move',
    #         'context': "{'move_type':'out_invoice'}",
    #         'type': 'ir.actions.act_window',
    #         'nodestroy': True,
    #         'target': 'current',
    #         'res_id': moves and moves.ids[0] or False,
    #     }


class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    default_customer_id = fields.Many2one('res.partner', string="Select Customer")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string="Analytic Tag")


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _validate_session(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        bank_payment_method_diffs = bank_payment_method_diffs or {}
        self.ensure_one()
        sudo = self.user_has_groups('point_of_sale.group_pos_user')
        if self.order_ids or self.statement_ids.line_ids:
            self.cash_real_transaction = self.cash_register_total_entry_encoding
            self.cash_real_expected = self.cash_register_balance_end
            self.cash_real_difference = self.cash_register_difference
            if self.state == 'closed':
                raise UserError(_('This session is already closed.'))
            self._check_if_no_draft_orders()
            self._check_invoices_are_posted()
            if self.update_stock_at_closing:
                self._create_picking_at_end_of_session()
                self.order_ids.filtered(lambda o: not o.is_total_cost_computed)._compute_total_cost_at_session_closing(
                    self.picking_ids.move_lines)
            try:
                data = self.with_company(self.company_id)._create_account_move(balancing_account, amount_to_balance,
                                                                               bank_payment_method_diffs)
            except AccessError as e:
                if sudo:
                    data = self.sudo().with_company(self.company_id)._create_account_move(balancing_account,
                                                                                          amount_to_balance,
                                                                                          bank_payment_method_diffs)
                else:
                    raise e

            try:
                balance = sum(self.move_id.line_ids.mapped('balance'))
                self.move_id._check_balanced()
            except UserError:
                # Creating the account move is just part of a big database transaction
                # when closing a session. There are other database changes that will happen
                # before attempting to create the account move, such as, creating the picking
                # records.
                # We don't, however, want them to be committed when the account move creation
                # failed; therefore, we need to roll back this transaction before showing the
                # close session wizard.
                self.env.cr.rollback()
                return self._close_session_action(balance)

            if self.move_id.line_ids:
                self.move_id.sudo().with_company(self.company_id)._post()
                # Set the uninvoiced orders' state to 'done'
                self.env['pos.order'].search([('session_id', '=', self.id), ('state', '=', 'paid')]).write(
                    {'state': 'done'})
            else:
                self.move_id.sudo().unlink()
            self.sudo().with_company(self.company_id)._reconcile_account_move_lines(data)
            analytic_account_id = self.config_id.analytic_account_id.id if self.config_id and self.config_id.analytic_account_id else False
            analytic_tag_ids = [(6, 0,
                                 self.config_id.analytic_tag_ids.ids)] if self.config_id and self.config_id.analytic_tag_ids else [
                (6, 0, [])]
            for move in self._get_related_account_moves():
                for line in move.line_ids:
                    line.sudo().write({
                        'analytic_account_id': analytic_account_id,
                        'analytic_tag_ids': analytic_tag_ids,
                    })
        else:
            statement = self.cash_register_id
            if not self.config_id.cash_control:
                statement.write({'balance_end_real': statement.balance_end})
            statement.button_post()
            statement.button_validate()
        self.write({'state': 'closed'})
        return True
