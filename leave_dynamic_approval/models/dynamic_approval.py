# -*- coding: utf-8 -*-

from odoo import models, api


class DynamicApproval(models.Model):
    _inherit = 'dynamic.approval'

    # @api.model
    # def _get_approval_validation_model_names(self):
    #     res = super()._get_approval_validation_model_names()
    #     res.append('hr.leave')
    #     return res
