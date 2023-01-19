from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    # def get_picking(self):
    #     domain = []
    #     if self.env.user.has_group('taqat_pos_extended.taqat_group_pos_user') and self.env.user and self.env.user.pos_config_ids:
    #         domain.append(('code', '=', 'internal'))
    #         location_ids = self.env.user.pos_config_ids.mapped('warehouse_id').mapped('lot_stock_id.id')
    #         if location_ids:
    #             domain.append(('warehouse_id.lot_stock_id.id', 'in', location_ids))
    #         return domain
    #     else:
    #         return domain

    # picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', required=True, readonly=True, states={'draft': [('readonly', False)]}, domain=get_picking)

    def button_validate(self):
        if self.location_dest_id and self.env.user and self.env.user.has_group('taqat_pos_extended.taqat_group_pos_user'):
            if self.location_dest_id.id not in self.env.user.pos_config_ids.mapped('picking_type_id').mapped('warehouse_id').mapped('lot_stock_id.id'):
                raise UserError(_("You are not allowed to validate."))
        res = super(StockPickingInherit, self).button_validate()
        return res

    