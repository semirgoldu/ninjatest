# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class ContractInherit(models.Model):
    _inherit = 'hr.contract'

    payroll_grade = fields.Selection(
        string='Payroll Grade',
        selection=[('1', 'Grade 1'),
                   ('2', 'Grade 2'), ('3', 'Grade 3')],
        required=False, related="job_id.payroll_grade")

    @api.onchange('wage','accommodation','mobile_allowance','food_allowance','transport_allowance','living_allowance','other_allowance')
    def _calculate_package(self):
        for rec in self:
            total = 0
            total += rec.wage or 0
            total += rec.accommodation or 0
            total += rec.mobile_allowance or 0
            total += rec.food_allowance or 0
            total += rec.transport_allowance or 0
            total += rec.living_allowance or 0
            total += rec.other_allowance or 0
            rec.package = total

    package = fields.Monetary('Package',
                              default=0.0,
                              help="Employee's Package.")
    accommodation = fields.Monetary('Housing Allowance',
                                    default=0.0,
                                    required=True,
                                    tracking=True,
                                    help="Employee's Accommodation.")

    mobile_allowance = fields.Monetary('Mobile Allowance',
                                       default=0.0,
                                       required=True,
                                       tracking=True,
                                       )

    food_allowance = fields.Monetary('Food Allowance',
                                     default=0.0,
                                     required=True,
                                     tracking=True,
                                     )
    transport_allowance = fields.Monetary('Transport Allowance',
                                          default=0.0,
                                          required=True,
                                          tracking=True,
                                          )
    living_allowance = fields.Monetary('Living Allowance',
                                       default=0.0,
                                       required=True,
                                       tracking=True,
                                       )
    other_allowance = fields.Monetary('Other Allowance',
                                      default=0.0,
                                      required=True,
                                      tracking=True,
                                      )

    maximum_ticket_allowance = fields.Monetary('Maximum Ticket Allowance',
                                               default=4500.0,
                                               required=True,
                                               tracking=True,
                                               )
    eligible_after = fields.Integer('Eligible After')
    eligible_every_year = fields.Integer('eligible every/year')
    wage_rate = fields.Float(
        string='Wage Rate',
        default=60,
        required=True)

    @api.constrains('wage_rate')
    def _check_payment_date(self):
        for record in self:
            if record.wage_rate > 100 or record.wage_rate < 0:
                raise ValidationError(_("Rate Must be between 0 and 100"))



    @api.onchange('wage')
    def _calculate_wage(self):
        if self.package and self.wage:
            if self.package != 0.0 and self.wage != 0.0:
                self.accommodation = self.package - self.wage
