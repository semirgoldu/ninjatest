from odoo import fields, models, api


class SmsConnectSource(models.Model):
	_name="sms.connect.source"

	name=fields.Char()
	source=fields.Char()
	mask=fields.Char()

	#    Fieldname = self.env['ir.config_parameter'].sudo().get_param('module_name.field_name')

