from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    dob = fields.Date("Date Of Birth")
    is_phone_verify = fields.Boolean("Is Phone Verify")
    is_email_verify = fields.Boolean("Is Email Verify")
    is_terms_condition_apply = fields.Boolean("Is Terms Condition Apply")
    gender = fields.Selection(string='Gender', selection=[('male', 'Male'), ('female', 'Female'), ], )
    building = fields.Char(string='Building')

    @api.model
    def signup_retrieve_info(self, token):
        # retrieve signup data on reset password.
        res = super(ResPartnerInherit, self).signup_retrieve_info(token)
        partner = self._signup_retrieve_partner(token, raise_exception=True)
        res['phone'] = partner.phone
        res['dob'] = partner.dob
        res['gender'] = partner.gender
        res['is_terms_condition_apply'] = partner.is_terms_condition_apply
        return res

    # removing constrain of vat field from website
    @api.constrains('vat', 'country_id')
    def check_vat(self):
        # The context key 'no_vat_validation' allows you to store/set a VAT number without doing validations.
        # This is for API pushes from external platforms where you have no control over VAT numbers.
        if self.env.context.get('no_vat_validation'):
            return
        if 'website_id' in self._context and self._context.get('website_id') == 1:
            return
        else:
            for partner in self:
                country = partner.commercial_partner_id.country_id
                if partner.vat and self._run_vat_test(partner.vat, country, partner.is_company) is False:
                    partner_label = _("partner [%s]", partner.name)
                    msg = partner._build_vat_error_message(country and country.code.lower() or None, partner.vat,
                                                           partner_label)
                    raise ValidationError(msg)
