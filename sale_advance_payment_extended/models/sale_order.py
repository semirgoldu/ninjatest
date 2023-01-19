from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    advance_done = fields.Boolean(string="Advance Payment", default=False, copy=False)
    partner_credit = fields.Monetary(related='partner_id.advance_amount', string="Remaining Partner Credit")

    def action_confirm(self):
        self.ensure_one()
        if self.partner_id and self.partner_id.advance_amount < self.amount_total:
            raise UserError(_("Order amount in greater than partner credit."))
        res = super(SaleOrderInherit, self).action_confirm()
        return res

    def action_advance_payment(self):
        view = self.env.ref('sale_advance_payment_extended.view_advance_payment_wizard')
        return {
            'name': _('Advance Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'advance.payment.wizard',
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_partner_id': self.partner_id.id},
        }
