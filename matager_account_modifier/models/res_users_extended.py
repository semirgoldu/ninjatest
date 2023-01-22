from odoo import fields, models, api


class MetagerResUsers(models.Model):
    _inherit = 'res.users'

    dob = fields.Date("Date Of Birth")
    is_phone_verify = fields.Boolean("Is Phone Verify")
    is_email_verify = fields.Boolean("Is Email Verify")
    is_terms_condition_apply = fields.Boolean("Is Terms Condition Apply")
    gender = fields.Selection(string='Gender', selection=[('male', 'Male'), ('female', 'Female'), ], )
    email_verification_code = fields.Char("Email Verification")
    phone_verification_code = fields.Char("Phone Verification")
    phone_otp_ids = fields.One2many(comodel_name='otp.phonenumber', inverse_name='user_id', string='Phone OTP', )
    email_otp_ids = fields.One2many(comodel_name='otp.email', inverse_name='user_id', string='Email OTP', )

    @api.model
    def _get_login_domain(self, login):
        # Login with phone or email added domain
        res = super(MetagerResUsers, self)._get_login_domain(login)
        res.insert(0, ('phone', '=', login))
        res.insert(0, '|')
        return res

    @api.model
    def create(self, vals):
        # set data in partner on create of user
        res = super(MetagerResUsers, self).create(vals)
        # if shop address verify partner email so no need to verify in email
        if res.partner_id.is_email_verify == True:
            res.is_email_verify = res.partner_id.is_email_verify
        if res.partner_id.is_phone_verify == True:
            res.is_phone_verify = res.partner_id.is_phone_verify
        # ---------------------------------------------
        if res.dob:
            res.partner_id.dob = res.dob
        if res.is_phone_verify:
            res.partner_id.is_phone_verify = res.is_phone_verify
        if res.is_email_verify:
            res.partner_id.is_email_verify = res.is_email_verify
        if res.gender:
            res.partner_id.gender = res.gender
        if res.gender:
            res.partner_id.is_terms_condition_apply = res.is_terms_condition_apply
        return res

    def write(self, vals):
        # set data in partner on update of user.
        res = super(MetagerResUsers, self).write(vals)
        if 'dob' in vals:
            self.partner_id.dob = self.dob
        if 'is_phone_verify' in vals:
            self.partner_id.is_phone_verify = self.is_phone_verify
        if 'is_email_verify' in vals:
            self.partner_id.is_email_verify = self.is_email_verify
        if 'gender' in vals:
            self.partner_id.gender = self.gender
        if 'is_terms_condition_apply' in vals:
            self.partner_id.is_terms_condition_apply = self.is_terms_condition_apply
        return res


class OTPPhonenumber(models.Model):
    _name = 'otp.phonenumber'

    date = fields.Datetime(string='Date')
    otp = fields.Char(string='OTP')
    user_id = fields.Many2one("res.users")


class OTPEmail(models.Model):
    _name = 'otp.email'

    date = fields.Datetime(string='Date')
    otp = fields.Char(string='OTP')
    user_id = fields.Many2one("res.users")
