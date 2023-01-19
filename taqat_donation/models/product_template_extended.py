from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ApprovalRequest(models.Model):
    _inherit = 'product.template'

    is_donation_generic = fields.Boolean("Donation Generic")
    is_wholesale = fields.Boolean("Wholesale")
    is_scrap = fields.Boolean("Scrap")
    is_convertable = fields.Boolean("Convertable")
    container_id = fields.Many2one('donation.containers', string="Container Number")

    @api.constrains('is_wholesale')
    def check_is_wholesale(self):
        for rec in self:
            wholesale_product = self.env['product.template'].sudo().search(
                [('is_wholesale', '=', True), ('id', '!=', rec.id)])
            if wholesale_product and rec.is_wholesale:
                raise UserError(_("Product Wholesale already exists.."))

    @api.constrains('is_convertable')
    def check_is_convertable(self):
        for rec in self:
            convertable_product = self.env['product.template'].sudo().search(
                [('is_convertable', '=', True), ('id', '!=', rec.id)])
            if convertable_product and rec.is_convertable:
                raise UserError(_("Product Convertable already exists.."))

    @api.constrains('is_scrap')
    def check_is_scrap(self):
        for rec in self:
            is_scrap = self.env['product.template'].sudo().search([('is_scrap', '=', True), ('id', '!=', rec.id)])
            if is_scrap and rec.is_scrap:
                raise UserError(_("Product Scrap already exists.."))
