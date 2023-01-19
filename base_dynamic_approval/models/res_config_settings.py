from odoo import api, fields, models
from odoo.addons.base.models.res_partner import _tz_get


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    email_resource_calendar_id = fields.Many2one(comodel_name='resource.calendar', )
    # number_of_hours_approve = fields.Selection([
    #     ('24_hour', '24 Hours'),
    #     ('48_hour', '48 Hours'),
    # ], string="Automatically Approve Hours",
    #     config_parameter='base_dynamic_approval.number_of_hours_approve')

    number_of_hours = fields.Integer(string="Automatically Approve Hours",
                                     config_parameter='base_dynamic_approval.number_of_hours')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        calendar_value = self.env['ir.config_parameter'].sudo().get_param(
            'base_dynamic_approval.email_resource_calendar_id')
        calendar_value = int(calendar_value) if calendar_value else False
        res.update(
            email_resource_calendar_id=calendar_value
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        email_resource_calendar_id = self.email_resource_calendar_id.id or False

        param.set_param(
            'base_dynamic_approval.email_resource_calendar_id',
            email_resource_calendar_id)
