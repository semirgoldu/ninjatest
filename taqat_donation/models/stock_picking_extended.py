import datetime

from odoo import models, fields, api, _
from collections import Counter, defaultdict
from odoo.exceptions import UserError


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    donation_order_id = fields.Many2one("donation.order", 'Donation Order')
    container_order_id = fields.Many2one("container.order", 'Container Order')
    is_open_get_donation_product = fields.Boolean(default=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")

    @api.model
    def default_get(self, fields):
        res = super(StockPickingInherit, self).default_get(fields)
        if self.env.user:
            res.update({'partner_id': self.env.user.partner_id.id if self.env.user and self.env.user.partner_id else False})
        return res

    def action_custom_confirm(self):
        self.ensure_one()
        self.state = 'confirm'

    @api.depends('state')
    def _compute_show_validate(self):
        for picking in self:
            if not (picking.immediate_transfer) and picking.state == 'draft':
                picking.show_validate = False
            elif picking.state not in ('draft', 'waiting', 'confirmed', 'confirm'):
                picking.show_validate = False
            else:
                picking.show_validate = True

    def action_confirm(self):
        if self.is_open_get_donation_product and self.donation_order_id.is_container:
            # self.is_open_get_donation_product = False
            return self.sudo().open_get_donation_product()
        else:
            return super(StockPickingInherit, self).action_confirm()

    def open_get_donation_product(self):
        action = self.env.ref('taqat_donation.action_donation_product').read()[0]
        action['context'] = {
            'stock_picking_id': self.id,
        }
        return action


class LotSeq(models.Model):
    _name = 'lot.seq'
    _description = 'Lot Sequence'

    sequence_code = fields.Char(copy=False, index=True, required=True)


class ResCompany(models.Model):
    _inherit = 'res.company'

    sequence_code = fields.Char(copy=False, index=True)


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    price_unit = fields.Float(string="Price Unit")
    # location_id = fields.Many2one("stock.location", related="location_dest_id", readonly=False)
    is_generate = fields.Boolean(default=False)

    def action_print_label(self):
        view = self.env.ref('stock.product_label_layout_form_picking')
        return {
            'name': _('Choose Labels Layout'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.label.layout',
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': {
                'default_product_ids': self.product_id.ids,
                'default_move_line_ids': self.move_line_ids.ids,
                'default_picking_quantity': 'picking'},
        }

    def action_show_details(self):
        res = super(StockMoveInherit, self).action_show_details()
        self.ensure_one()
        if self.env.company and self.env.company.sequence_code:
            self.next_serial = self.env.company.sequence_code
        else:
            self.next_serial = self.env.ref('taqat_donation.sequence_self_lot_sequence').next_by_code(sequence_code="lot.seq")
        return res

    def _generate_serial_numbers(self, next_serial_count=False):
        res = super(StockMoveInherit, self)._generate_serial_numbers(next_serial_count)
        if self.next_serial_count:
            for i in range(0, self.next_serial_count):
                self.next_serial = self.env.ref('taqat_donation.sequence_self_lot_sequence').next_by_code(
                    sequence_code="lot.seq")
                self.env.company.sudo().write({'sequence_code': self.next_serial})
        self.is_generate = True
        return res

    def action_clear_lines_show_details(self):
        res = super(StockMoveInherit, self).action_clear_lines_show_details()
        self.is_generate = False
        return res

    def action_assign_price_unit(self):
        self.ensure_one()
        if not self.price_unit:
            raise UserError(_("You need to set a price_unit."))
        for rec in self.move_line_nosuggest_ids:
            rec.sudo().write({'price_unit': self.price_unit})
        for rec in self.move_line_ids:
            rec.sudo().write({'price_unit': self.price_unit})
        return self.action_show_details()

    def action_clear_price_unit(self):
        self.ensure_one()
        for rec in self.move_line_nosuggest_ids:
            rec.sudo().write({'price_unit': 0.0})
        for rec in self.move_line_ids:
            rec.sudo().write({'price_unit': 0.0})
        return self.action_show_details()

    def action_assign_location(self):
        self.ensure_one()
        if not self.location_id:
            raise UserError(_("You need to set a Location."))
        for rec in self.move_line_nosuggest_ids:
            rec.sudo().write({'location_dest_id': self.location_id.id})
        for rec in self.move_line_ids:
            rec.sudo().write({'location_dest_id': self.location_id.id})
        return self.action_show_details()


class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'

    price_unit = fields.Float("Price Unit")

    # @api.constrains('lot_id')
    # def onchange_lot_id(self):
    #     for rec in self:
    #         domain = [('move_id', '=', rec.move_id.id), ('id', '!=', rec.id)]
    #         if rec.lot_id:
    #             domain.append(('lot_id', '=', rec.lot_id.id))
    #         move_lines = self.env['stock.move.line'].search(domain)
    #         if move_lines:
    #             raise UserError(_("%s is Used again." %move_lines.lot_id.name))

    def _create_and_assign_production_lot(self):
        """ Creates and assign new production lots for move lines."""
        lot_vals = []
        # It is possible to have multiple time the same lot to create & assign,
        # so we handle the case with 2 dictionaries.
        key_to_index = {}  # key to index of the lot
        key_to_mls = defaultdict(lambda: self.env['stock.move.line'])  # key to all mls
        for ml in self:
            key = (ml.company_id.id, ml.product_id.id, ml.lot_name)
            key_to_mls[key] |= ml
            if ml.tracking != 'lot' or key not in key_to_index:
                key_to_index[key] = len(lot_vals)
                lot_vals.append({
                    'company_id': ml.company_id.id,
                    'name': ml.lot_name,
                    'product_id': ml.product_id.id,
                    'price_unit': ml.price_unit
                })

        lots = self.env['stock.production.lot'].create(lot_vals)
        for key, mls in key_to_mls.items():
            mls._assign_production_lot(lots[key_to_index[key]].with_prefetch(
                lots._ids))  # With prefetch to reconstruct the ones broke by accessing by index


class StockPickingTypeInherit(models.Model):
    _inherit = 'stock.picking.type'

    operation_type = fields.Selection([('wholesale', 'Wholesale'), ('inspection', 'Inspection'), ('scrap', 'Scrap')],
                                      string="Container Operation Type")
    is_container_type = fields.Boolean(default=False, string="Is Container Type?")
