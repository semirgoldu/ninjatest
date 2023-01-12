from odoo import fields, models, api

class ResConfigSettingsInherit(models.TransientModel):
	_inherit = 'res.config.settings'

	application_name = fields.Char()
	application_password = fields.Char()
	application_url = fields.Char()
	
	def set_values(self):
		super(ResConfigSettingsInherit, self).set_values()
		param_obj = self.env['ir.config_parameter']
		param_obj.sudo().set_param('sms_connect_vodafone.application_name',self.application_name)
		param_obj.sudo().set_param('sms_connect_vodafone.application_password',self.application_password)
		param_obj.sudo().set_param('sms_connect_vodafone.application_url',self.application_url)
	
	@api.model
	def get_values(self):
		res = super(ResConfigSettingsInherit, self).get_values()
		param_obj = self.env['ir.config_parameter']
		res.update(application_name=param_obj.sudo().get_param('sms_connect_vodafone.application_name',default=''),
				   application_password=param_obj.sudo().get_param('sms_connect_vodafone.application_password',default=''),
				   application_url=param_obj.sudo().get_param('sms_connect_vodafone.application_url',default=''),

				   )
		return res