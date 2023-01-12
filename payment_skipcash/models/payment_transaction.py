# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Original Copyright 2015 Eezee-It, modified and maintained by Odoo.

import json
import logging
import hashlib
import hmac
import base64
import requests

from werkzeug import urls

from odoo import _, api, models
from odoo.exceptions import ValidationError

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_sips.controllers.main import SipsController
from .const import RESPONSE_CODES_MAPPING, SUPPORTED_CURRENCIES
import requests
  
# api-endpoint
URL = "https://connectsms.vodafone.com.qa/SMSConnect/SendServlet"

  

  




_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _compute_reference(self, provider, prefix=None, separator='-', **kwargs):
        """ Override of payment to ensure that Sips requirements for references are satisfied.

        Sips requirements for transaction are as follows:
        - References can only be made of alphanumeric characters.
          This is satisfied by forcing the custom separator to 'x' to ensure that no '-' character
          will be used to append a suffix. Additionally, the prefix is sanitized if it was provided,
          and generated with 'tx' as default otherwise. This prevents the prefix to be generated
          based on document names that may contain non-alphanum characters (eg: INV/2020/...).
        - References must be unique at provider level for a given merchant account.
          This is satisfied by singularizing the prefix with the current datetime. If two
          transactions are created simultaneously, `_compute_reference` ensures the uniqueness of
          references by suffixing a sequence number.

        :param str provider: The provider of the acquirer handling the transaction
        :param str prefix: The custom prefix used to compute the full reference
        :param str separator: The custom separator used to separate the prefix from the suffix
        :return: The unique reference for the transaction
        :rtype: str
        """
        if provider == 'skipcash':
            # We use an empty separator for cosmetic reasons: As the default prefix is 'tx', we want
            # the singularized prefix to look like 'tx2020...' and not 'txx2020...'.
            prefix = payment_utils.singularize_reference_prefix(separator='')
            separator = 'x'  # Still, we need a dedicated separator between the prefix and the seq.
        return super()._compute_reference(provider, prefix=prefix, separator=separator, **kwargs)

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Sips-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """

        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'skipcash':
            return res
        amnt = self.amount
        _logger.info('alloha')
        _logger.info(str(int(amnt)))
        name=self.partner_id.name
        params = "Uid=%s,KeyId=%s,Amount=%s,FirstName=%s,LastName=%s,Email=%s,TransactionId=%s" % (self.acquirer_id.skipcash_merchant_id,self.acquirer_id.skipcash_key_id,str(float(amnt)),name,name,self.partner_id.email,self.reference)
        #key = "hm9W0yYlU+gj2frCKjKb81uku7kM2eSs2+WYQ2L15853mOosHTvgHdJT0JuM0jGZykxKca0S+WuwE+XrorNxf0vPaYnbOh2z4SvSCxUH2jJEq/1vobdirWRrnXuDAxeRaCSsMbtHJh45TIgX7JS5RbXz7giQvg5pC3AilZiQ2d8TAtG231gGpMHI3wynoP6792UegIizzgFgAp7LYVfQ6q+47gdNW7YqQZN3mA9z6X+Sg1v3uH8r/XsNAhPOjs6iZ8TEBw+OwDRuW5G3QoQmNOmIjYT97VBbZpdhkFrYwmxbfHML6aTmD1Dcp2RJY8mVcCSBHQEMTCuYM9aHrNIxIPfR7h4rPVFscQctNBByxcbY/1IhXUPuxLqjIEiB2TryE7Tq72ug9dJgfxAIPRsq251qTQQzez0qrDaQ7K9CWf7wtguFs54Uj9ZXi3F3R+LeL+E7wgmU/PK5hkgHuDiy4n8yKQ91+ELLNtYcHcJWodbIHsZLLyGfpG0cZk9XpFVnCn0HFAp3w8Njiz9gM4oR/g=="
        base_url = self.get_base_url()
        data = {
            "uid":self.acquirer_id.skipcash_merchant_id,
            "keyId":self.acquirer_id.skipcash_key_id,
            "amount":"%s" % str(float(amnt)),
            "firstName":self.partner_id.name or '',
            "lastName":self.partner_id.name or '',
            "email":self.partner_id.email,
            'transactionId': self.reference,
        }
        _logger.info(data)
        encoded=self.acquirer_id._skipcash_generate_shasign(params)
        headers = {
            'Content-Type':"application/json",
            'Authorization':encoded,

        }
        #data = {
        #    'amount': payment_utils.to_minor_currency_units(self.amount, self.currency_id),
        #    'currencyCode': SUPPORTED_CURRENCIES[self.currency_id.name],  # The ISO 4217 code
        #    'merchantId': self.acquirer_id.sips_merchant_id,
        #    'normalReturnUrl': urls.url_join(base_url, SipsController._return_url),
        #    'automaticResponseUrl': urls.url_join(base_url, SipsController._notify_url),
        #    'transactionReference': self.reference,
        #    'statementReference': self.reference,
        #    'keyVersion': self.acquirer_id.sips_key_version,
        #    'returnContext': json.dumps(dict(reference=self.reference)),
        #}
        api_url = self.acquirer_id.skipcash_prod_url if self.acquirer_id.state == 'enabled' \
            else self.acquirer_id.skipcash_test_url
        try:
            response = requests.post(api_url,json=data,headers=headers)

            resx = json.loads(response.text)
            _logger.info(resx)
            url = resx['resultObj']['payUrl']
            #data = '|'.join([f'{k}={v}' for k, v in data.items()])
            
        except:
            raise ValidationError('An unexpected error happened please try again.')

        return {
                'api_url': url+'?name=skipcash',
                'Data':''
            }
    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        """ Override of payment to find the transaction based on Sips data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        :raise: ValidationError if the currency is not supported
        :raise: ValidationError if the amount mismatch
        """
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'skipcash':
            return tx

        #data = self._skipcash_data_to_object(data['Data'])
        reference = data.get('transId')

        if not reference:
            return_context = json.loads(data.get('returnContext', '{}'))
            reference = return_context.get('transId')

        tx = self.search([('reference', '=', reference), ('provider', '=', 'skipcash')])
        if not tx:
            raise ValidationError(
                "SKIPCASH: " + _("No transaction found matching reference %s.", reference)
            )

        #sips_currency = SUPPORTED_CURRENCIES.get(tx.currency_id.name)
        #if not sips_currency:
        #    raise ValidationError(
        #        "Sips: " + _("This currency is not supported: %s.", tx.currency_id.name)
        #    )

        #amount_converted = payment_utils.to_major_currency_units(
        #    float(data.get('amount', '0.0')), tx.currency_id
        #)
        #if tx.currency_id.compare_amounts(amount_converted, tx.amount) != 0:
        #    raise ValidationError(
        #        "Sips: " + _(
        #            "Incorrect amount: received %(received).2f, expected %(expected).2f",
        #            received=amount_converted, expected=tx.amount
        #        )
        #    )
        return tx

    def _process_feedback_data(self, data):
        """ Override of payment to process the transaction based on Sips data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        """
        super()._process_feedback_data(data)
        if self.provider != 'skipcash':
            return

        #data = self._sips_data_to_object(data.get('Data'))
        self.acquirer_reference = data.get('id')
        response_code = data.get('statusId')
        if response_code in RESPONSE_CODES_MAPPING['pending']:
            status = "1"
            self._set_pending()
        elif response_code in RESPONSE_CODES_MAPPING['done']:
            status = "2"
            self._set_done()
            # defining a params dict for the parameters to be sent to the API
            PARAMS = {'application':'http_gw1157','password':'bdeyc5h3','content':'Dear %s, Your order with transactin number %s is complete' % (self.partner_id.name,data.get('transId')),'destination':self.partner_id.phone,'source':'97433','mask':'OKSOUQ'}
  
            # sending get request and saving the response as response object
            r = requests.get(url = URL, params = PARAMS)
        elif response_code in RESPONSE_CODES_MAPPING['cancel']:
            status = "3"
            self._set_canceled()
        else:
            status = "5"
            self._set_error(_("Unrecognized response received from the payment provider."))
        _logger.info(
            "ref: %s, got response [%s], set as '%s'.", self.reference, response_code, status
        )

    def _skipcash_data_to_object(self, data):
        res = {}
        for element in data.split('|'):
            key, value = element.split('=')
            res[key] = value
        return res
