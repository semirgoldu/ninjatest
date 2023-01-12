# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Original Copyright 2015 Eezee-It, modified and maintained by Odoo.

from hashlib import sha256

from odoo import api, fields, models

import hashlib
import hmac
import base64
import requests
import json

from .const import SUPPORTED_CURRENCIES


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('skipcash', "SkipCash")], ondelete={'skipcash': 'set default'})
    skipcash_merchant_id = fields.Char(
        string="Merchant ID", help="The ID solely used to identify the merchant account with SkipCash",
        required_if_provider='skipcash')
    skipcash_key_id = fields.Char(
        string="Key ID", help="The ID solely used to identify the merchant account with SkipCash",
        required_if_provider='skipcash')
    skipcash_secret = fields.Char(
        string="SkipCash Secret Key", size=640, required_if_provider='skipcash', groups='base.group_system')
    skipcash_test_url = fields.Char(
        string="Test URL", required_if_provider='skipcash',
        default="https://skipcashtest.azurewebsites.net/api/v1/payments")
    skipcash_prod_url = fields.Char(
        string="Production URL", required_if_provider='skipcash',
        default="https://skipcashtest.azurewebsites.net/api/v1/payments")


    def _skipcash_generate_shasign(self, data):
        """ Generate the shasign for incoming or outgoing communications.

        Note: self.ensure_one()

        :param str data: The data to use to generate the shasign
        :return: shasign
        :rtype: str
        """
        self.ensure_one()

        key = self.skipcash_secret
        byte_key = bytes(key, 'UTF-8')
        message = data.encode()

        h = hmac.new(byte_key, message, hashlib.sha256).digest()


        encoded = base64.b64encode(h).decode()
        return encoded

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'skipcash':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_skipcash.payment_method_skipcash').id
