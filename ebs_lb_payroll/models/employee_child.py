# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class EmployeeChild(models.Model):
    _name = 'hr.emp.child'
    _description = 'Employee Child'

    name = fields.Char(
        string='Name',
        required=True)

    date_of_birth = fields.Date(
        string='Date of Birth',
        required=False)

    is_student = fields.Boolean(
        string='Is Student',
        required=False, default=False)

    emp_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=False)
