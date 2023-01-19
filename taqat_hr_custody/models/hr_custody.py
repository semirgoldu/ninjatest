from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrCustodyInherit(models.Model):
    _inherit = 'hr.custody'

    responsible_id = fields.Many2one("hr.employee", 'Responsible')
    

