from odoo import models, fields, api, _


class FleetOdometerInherit(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    type = fields.Selection([('on', 'ON'), ('off', 'OFF')], string="Type")

    def get_driver_name(self):
        if self.env.user.has_group('taqat_donation.group_driver'):
            return [('id', '=', self.env.user.partner_id.id)]
        else:
            return []

    @api.model
    def create(self, vals):
        res = super(FleetOdometerInherit, self).create(vals)
        last_type = self.search([('driver_id', '=', res.driver_id.id), ('id', '!=', res.id)], limit=1)
        if last_type.type == 'on':
            res['type'] = 'off'
        elif last_type.type == 'off':
            res['type'] = 'on'
        else:
            res['type'] = 'on'
        return res

    @api.model
    def default_get(self, fields):
        res = super(FleetOdometerInherit, self).default_get(fields)
        if self.env.user.has_group('taqat_donation.group_driver') and self.env.user and self.env.user.partner_id:
            res['driver_id'] = self.env.user.partner_id.id
            res['vehicle_id'] = self.env['fleet.vehicle'].sudo().search([('driver_id', '=', self.env.user.partner_id.id)], limit=1).id
        return res

    date = fields.Datetime("Date", default=lambda self: fields.Datetime.now(), readonly=True)
    driver_id = fields.Many2one("res.partner", related=False, string="Driver", readonly=False, domain=get_driver_name)
