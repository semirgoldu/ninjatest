from odoo import fields, models, api, _


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    def get_zero_qty_product_archive(self):
        all_products = self.env['product.product'].search([('qty_available', '<=', 0.0)])
        for prd in all_products:
            prd.action_archive()