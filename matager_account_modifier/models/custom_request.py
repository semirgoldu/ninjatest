from odoo import models, fields, api, _


class CustomRequest(models.Model):
    _name = 'custom.request'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users', string='User')
    partner_id = fields.Many2one('res.partner', string='Partner')
    text = fields.Text(string='Text')
