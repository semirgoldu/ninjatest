from odoo import fields, models, api, _


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    return_requested = fields.Boolean("Return Sale")
    gift_count = fields.Integer(compute="_compute_gift_count", string='Gift Count', copy=False, default=0, )

    def _compute_gift_count(self):
        for order in self:
            gift_cards = self.env['gift.card'].search(
                [('sale_order_id', '=', order.id), ('sale_order_id', '!=', False)])
            order.gift_count = len(gift_cards.ids)

    def action_view_gift_card(self):
        action = self.env["ir.actions.actions"]._for_xml_id("gift_card.gift_card_action")
        tree_view = (self.env.ref('gift_card.gift_card_view_tree').id, 'tree')
        form_view = (self.env.ref('gift_card.gift_card_view_form').id, 'form')
        action['views'] = [tree_view,form_view]
        action['view_mode'] = 'form'
        action['domain'] = [('sale_order_id', '=', self.id), ('sale_order_id', '!=', False)]
        return action

    def return_sale_order(self, token):
        return '%s?access_token=%s' % (str(self.id), token)

    def button_create_gift_card(self):
        gift_cart_form_view_id = self.env.ref('gift_card.gift_card_view_form')
        return {
            'name': _('Gift Card'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'gift.card',
            'views': [(gift_cart_form_view_id.id, 'form')],
            'view_id': gift_cart_form_view_id.id,
            'target': 'new',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_initial_amount': self.amount_total,
                'default_sale_order_id': self.id,
                'partner_readonly': True,
                'expire_date_readonly': True,
                'create': False,
            }
        }
