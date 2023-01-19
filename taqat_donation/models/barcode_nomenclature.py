from odoo import models, fields, api, _


class BarcodeNomenclatureInherit(models.Model):
    _inherit = 'barcode.nomenclature'

    donation_order_id = fields.Many2one("donation.order", 'Donation Order')
    is_open_get_donation_product = fields.Boolean(default=True)

    def action_confirm(self):
        if self.is_open_get_donation_product == True:
            self.is_open_get_donation_product = False
            return self.open_get_donation_product()
        else:
            return super(StockPickingInherit, self).action_confirm()

    def open_get_donation_product(self):
        action = self.env.ref('taqat_donation.action_donation_product').read()[0]
        action['context'] = {
            'stock_picking_id': self.id,
        }
        return action
