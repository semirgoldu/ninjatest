# -*- coding: utf-8 -*-
from odoo import models, fields


class HelpdesksCustomNew(models.Model):
    _inherit = 'helpdesk.ticket'

    account_asset_asset_id= fields.Many2one(
        comodel_name='account.asset.asset',
        string='Property',
        store=True)

    maintenance_ids = fields.One2many('maintenance.request', 'ticket_id', string="Maintenance Request")


class MaintenanceRequestExt(models.Model):
    _inherit = 'maintenance.request'

    ticket_id = fields.Many2one('helpdesk.ticket', string="Ticket")