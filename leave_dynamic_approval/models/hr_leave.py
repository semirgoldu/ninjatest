# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class HrLeave(models.Model):
    _name = 'hr.leave'
    _inherit = ['hr.leave', 'dynamic.approval.mixin']
    _state_from = ['draft', 'confirm']
    _state_to = ['validate1', 'validate']

    # def create(self, vals):
    #     res = super(HrLeave, self).create(vals)
    #     res.action_dynamic_approval_request()
    #     return res

    # @api.model
    # def _get_under_validation_exceptions(self):
    #     res = super(HrLeave, self)._get_under_validation_exceptions()
    #     return res + [
    #         'no_allocation',
    #         'leave_wage',
    #         'leave_accommodation',
    #         'leave_mobile_allowance',
    #         'leave_transport_allowance',
    #         'leave_social_allowance',
    #         'leave_other_allowance',
    #         'total_amount',
    #         'approve_validate'
    #     ]
