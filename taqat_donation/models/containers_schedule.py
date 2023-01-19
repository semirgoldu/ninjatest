from odoo import models, fields, api, _
from datetime import datetime
import itertools
from odoo.exceptions import UserError


class ContainersSchedule(models.Model):
    _name = 'containers.schedule'
    _rec_name = 'driver_id'

    driver_id = fields.Many2one("res.partner", "Driver", domain=[('is_driver', '=', True)])
    day_of_week_ids = fields.Many2many('containers.schedule.week', string="Day of week")
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    container_ids = fields.One2many('container.schedule', 'cs_id')
    containers_ids = fields.Many2many('donation.containers', 'donation_containers_rel', 'donation_containers_col',
                                      'donation_containers_col2', string="Containers")
    containers_id = fields.Many2one('donation.containers', string="Containers old")

    # @api.model
    # def _create_donation_order(self):
    #     containers = self.sudo().search([])
    #     donation_order = self.env['donation.order']
    #     for container in containers:
    #         if container.from_date and container.to_date and container.day_of_week_ids and container.from_date <= datetime.today().date() and container.to_date >= datetime.today().date() and str(
    #                 datetime.today().isoweekday()) in [x for x in container.day_of_week_ids.mapped('code')]:
    #             donation_type = self.env['donation.type'].sudo().search([('is_container', '=', True)], limit=1)
    #             for rec in container.containers_ids:
    #                 vals = {
    #                     'order_date': datetime.today().date(),
    #                     'driver_id': container.driver_id.id if container.driver_id else False,
    #                     'donation_type': donation_type.id if donation_type else False,
    #                     'donation_order_containers_ids': [(0, 0, {"container_id": rec.id})]
    #                 }
    #                 donation_order.sudo().create(vals)

    @api.model
    def _create_donation_order(self):
        all_containers = self.sudo().search([])
        donation_order = self.env['donation.order']
        donation_type = self.env['donation.type'].sudo().search([('is_container', '=', True)], limit=1)
        for containers in all_containers:
            if containers.from_date and containers.to_date and containers.from_date <= datetime.today().date() and containers.to_date >= datetime.today().date():
                for rec in containers.container_ids:
                    if str(datetime.today().isoweekday()) in [x for x in rec.day_of_week_ids.mapped('code')]:
                        for r in rec.containers_ids:
                            vals = {
                                'order_date': datetime.today().date(),
                                'driver_id': containers.driver_id.id if containers.driver_id else False,
                                'donation_type': donation_type.id if donation_type else False,
                                'donation_order_containers_ids': [(0, 0, {"container_id": r.id})]
                            }
                            donation_order.sudo().create(vals)

    @api.constrains('container_ids')
    def check_containers_ids(self):
        combinations = []
        for container in self.container_ids:
            c_list = self.get_combination(container.containers_ids.ids,
                                          container.day_of_week_ids.ids)
            if combinations:
                if set(c_list).intersection(combinations):
                    raise UserError(_("Same container found on same day."))
            combinations += c_list

    def get_combination(self, container, days):
        return list(itertools.product(container, days))


class ContainersScheduleWeek(models.Model):
    _name = 'containers.schedule.week'

    name = fields.Char("Name")
    code = fields.Char("Code")


class ContainerSchedule(models.Model):
    _name = 'container.schedule'

    cs_id = fields.Many2one('containers.schedule')
    containers_ids = fields.Many2many('donation.containers', 'donation_container_rel', 'donation_container_col',
                                      'donation_container_col2', string="Containers")
    day_of_week_ids = fields.Many2many('containers.schedule.week', string="Day of week")
