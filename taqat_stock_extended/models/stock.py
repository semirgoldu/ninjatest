from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    from_serial_number = fields.Char(string="From Serial Number")
    to_serial_number = fields.Char(string="To Serial Number")

    def action_assign_serial_number(self):
        self.ensure_one()
        if not self.from_serial_number or not self.to_serial_number:
            raise UserError(_("You need to set from and to number."))
        if self.location_id and self.location_dest_id:
            from_number,to_number = int(self.from_serial_number),int(self.to_serial_number)
            for i in range(from_number, to_number+1):
                lot = self.env['stock.production.lot'].sudo().search([('name', '=', i), ('product_id', '=', self.product_id.id)])
                if not lot:
                    raise UserError(_("%s lot/serial number not found." %(i)))
                if lot:
                    move_line_vals = {
                        'picking_id': self.picking_id.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'product_id': self.product_id.id,
                        'product_uom_id': self.product_id.uom_id.id,
                        'qty_done': 1,
                        'lot_id': lot.id,
                        'move_id': self.id,
                    }
                    self.sudo().write({'move_line_ids': [(0, 0, move_line_vals)]})
                    i = i + 1
        return self.action_show_details()

    def action_clear_serial_number(self):
        self.ensure_one()
        self.sudo().write({'move_line_ids': [(5, 0,)]})
        return self.action_show_details()
