from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    zk_url = fields.Char(string="ZK Base URL")
    last_id = fields.Integer(string="Last ID")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        select_type = self.env['ir.config_parameter'].sudo()
        select_type.set_param('res.config.settings.zk_url', self.zk_url)
        select_type.set_param('res.config.settings.last_id', self.last_id)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        select_type = self.env['ir.config_parameter'].sudo()
        zk_url = select_type.get_param('res.config.settings.zk_url')
        last_id = select_type.get_param('res.config.settings.last_id')
        res.update({'zk_url': zk_url, 'last_id': last_id})
        return res
