import json
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    lot_data_json = fields.Char(
        "Lot data dict",
        help="Technical field: Used in POS frontend to search products by Lotinfo",
        compute="_compute_lot_data_json",
    )

    def _compute_lot_data_json(self):
        for rec in self:
            rec.lot_data_json = json.dumps(
                [
                    {
                        "lot_name": s.name,
                    }
                    for s in self.env['stock.production.lot'].sudo().search([('product_id.product_tmpl_id', '=', rec.id)])
                ]
            )