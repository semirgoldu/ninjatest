from odoo import fields, models, api
from odoo.exceptions import ValidationError,UserError
import requests
import json

class SmsConnectSms(models.Model):
	_name="sms.connect.sms"
	STATE=[
		('draft','New'),
		('sent','Sent'),
		('cancel','Cancel'),
		('error','Error')
	]
	name=fields.Char()
	date=fields.Datetime(default=fields.Datetime.now())
	source=fields.Many2one('sms.connect.source')
	ttype=fields.Selection([('number','Number'),('contact','Contact')],default="contact")
	number=fields.Char()
	contact=fields.Many2one('res.partner')
	content=fields.Text()
	state=fields.Selection(STATE,default='draft')
	result=fields.Text()


	def send_sms(self):
		app_url = self.env['ir.config_parameter'].sudo().get_param('sms_connect_vodafone.application_url')
		app_name = self.env['ir.config_parameter'].sudo().get_param('sms_connect_vodafone.application_name')
		app_password = self.env['ir.config_parameter'].sudo().get_param('sms_connect_vodafone.application_password')
		if not app_url or not app_name or not app_password:
			raise ValidationError('Please configure your SMS Connect Application First')

		if self.ttype == 'contact' and not self.contact.mobile:
			raise ValidationError('Please add a phone numbe to the contact you selected')

		number = self.contact.mobile if self.ttype == 'contact' else self.number

		PARAMS = {
			'application':app_name,
			'password':app_password,
			'content':self.content,
			'destination':number,
			'source':self.source.source,
			'mask':self.source.mask
			}
		try:
			r = requests.get(url = app_url, params = PARAMS)
  

			data = r.json()

			self.write({'result':json.dumps(data)})
			self.write({'state':'sent'})
		except:
			self.write({'state':'error'})
		
	def cancel_sms(self):
		pass
	def retry_sms(self):
		self.send_sms()