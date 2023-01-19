from odoo import _, api, fields, models


class CompoundUtility(models.Model):
    _name = "compound.utility"
    _description = 'Compound Utility'

    name = fields.Char(string="Name")


class CompoundUtilityLines(models.Model):
    _name = "compound.utility.line"
    _description = 'Compound Utility'
    _rec_name = 'compound_utility_id'

    note = fields.Text(
        string='Remarks')
    ref = fields.Char(
        string='Reference',
        size=60)
    # expiry_date = fields.Date(
    #     string='Expiry Date')
    # issue_date = fields.Date(
    #     string='Issuance Date')
    compound_utility_id = fields.Many2one(
        comodel_name='compound.utility',
        string='Common Area')
    compound_property_id = fields.Many2one(
        comodel_name='account.asset.asset',
        string='Property')
    contact_id = fields.Many2one(
        comodel_name='tenant.partner',
        string='Contact',
        domain="[('tenant', '=', True)]")