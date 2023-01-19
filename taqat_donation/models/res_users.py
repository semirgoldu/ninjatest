from odoo import models, fields, api, _


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    is_driver = fields.Boolean(default=False, string="Is Driver?")

    @api.model
    def create(self, vals):
        res = super(ResUsersInherit, self).create(vals)
        if 'is_driver' in vals:
            res.partner_id.sudo().write({'is_driver': vals.get('is_driver')})
        return res

    def write(self, vals):
        res = super(ResUsersInherit, self).write(vals)
        if 'is_driver' in vals:
            self.partner_id.sudo().write({'is_driver': vals.get('is_driver')})
        return res

    def unlink(self):
        if self.partner_id:
            self.partner_id.sudo().write({'is_driver': False})
        res = super(ResUsersInherit, self).unlink()
        return res


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    is_driver = fields.Boolean()
