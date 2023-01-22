from odoo import fields, models, api


class MatagerResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    resend_opt_time = fields.Float("Resend OTP Time", related='company_id.resend_opt_time', readonly=False)


class MatagerResCompany(models.Model):
    _inherit = 'res.company'

    resend_opt_time = fields.Float("Resend OTP Time", default=2.0)
