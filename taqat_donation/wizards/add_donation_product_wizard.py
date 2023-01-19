# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class DonationProduct(models.Model):
    _name = 'donation.product'

    donation_product_line_ids = fields.One2many("donation.product.line","donation_product_id")

    def add_product(self):
        picking_id = self.env['stock.picking'].browse(int(self._context.get('stock_picking_id')))
        for rec in picking_id.move_ids_without_package:
            rec.sudo().write({'state': 'draft'})
        picking_id.move_ids_without_package = [(5, 0, 0)]
        picking_id.is_open_get_donation_product = False
        picking_id.write({'move_ids_without_package':[
            (0, 0, {'product_id': rec.product_id.product_variant_id.id if rec.product_id.product_variant_id else False,
                    'product_uom_qty': rec.qty,
                    'description_picking': rec.product_id.name,
                    'name': rec.product_id.name,
                    'product_uom': rec.product_id.uom_id.id,
                    'location_id': picking_id.location_id.id,
                    'location_dest_id': picking_id.location_dest_id.id, })for rec in self.donation_product_line_ids]})
        picking_id.action_confirm()


class DonationProductLine(models.Model):
    _name = 'donation.product.line'

    product_id = fields.Many2one("product.template", "Product")
    qty = fields.Float("Quantity")
    donation_product_id = fields.Many2one("donation.product")