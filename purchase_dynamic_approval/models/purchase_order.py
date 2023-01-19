# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'dynamic.approval.mixin']
    _state_from = ['draft']
    _state_to = ['sent', 'to_approve', 'purchase', 'done']
