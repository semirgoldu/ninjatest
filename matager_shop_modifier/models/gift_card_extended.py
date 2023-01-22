from odoo import fields, models, api, _
import time
import string
import secrets


class GiftCardInherit(models.Model):
    _inherit = 'gift.card'

    sale_order_id = fields.Many2one("sale.order","Sale Order")

    def generateGiftCardCodes(self):
        seconds = time.time()
        unix_time_to_string = str(seconds).split('.')[0]  # time.time() generates a float example 1596941668.6601112
        alphaNumeric = string.ascii_uppercase + unix_time_to_string
        firstSet = ''.join(secrets.choice(alphaNumeric) for i in range(4))
        secondSet = ''.join(secrets.choice(alphaNumeric) for i in range(4))
        thirdSet = ''.join(secrets.choice(alphaNumeric) for i in range(4))
        giftCardCode = firstSet + "-" + secondSet + "-" + thirdSet
        return giftCardCode

    @api.model
    def _generate_code(self):
        return self.generateGiftCardCodes()
