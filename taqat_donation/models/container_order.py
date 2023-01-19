import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from lxml import etree


class ContainerOrder(models.Model):
    _name = 'container.order'
    _rec_name = 'container_id'

    date = fields.Date(string="Date")
    container_id = fields.Many2one("donation.containers", string="Container Number")
    order_number = fields.Many2one("donation.order", string="Donation Order Number")
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')
    driver_id = fields.Many2one("res.partner", "Driver")
    owner_id = fields.Many2one("res.users", "Owner")
    total_weight = fields.Float(string="Total Weight")
    order_lines = fields.One2many("container.order.line", "container_order_id", string="Order Lines")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled')], default='draft', track_visibility='onchange',
        string='Status', required=True, readonly=True, index=True)
    order_count = fields.Integer(compute="get_order_count")
    parent_id = fields.Many2one("container.order")
    can_confirm = fields.Boolean(compute="get_can_confirm")
    is_created_by_donation = fields.Boolean(default=False)
    is_wholesale = fields.Boolean(default=False, compute="get_is_wholesale", store=True)
    inspection_user_id = fields.Many2one('res.users', "Inspection User", domain=lambda self: [
        ("groups_id", "in", [self.env.ref("taqat_groups_access_rights_extended.taqat_group_inspection_user").id])])

    def get_can_confirm(self):
        for rec in self:
            rec.can_confirm = False
            if rec.parent_id and rec.inspection_user_id:
                if rec.inspection_user_id.id == rec.env.uid:
                    rec.can_confirm = True
            elif not rec.parent_id:
                if rec.owner_id.id == rec.env.uid or self.env.user.has_group('taqat_groups_access_rights_extended.taqat_group_inventory_manager_role') or self.env.user.has_group('taqat_groups_access_rights_extended.taqat_group_inventory_clerk'):
                    rec.can_confirm = True

    def action_get_donation_transfer_view(self):
        self.ensure_one()
        res = self.env["ir.actions.actions"].sudo()._for_xml_id("stock.action_picking_tree_all")
        res['domain'] = [('donation_order_id', 'in', self.order_number.ids)]
        res['context'] = {'container_order_id': self.id}
        return res

    @api.depends('picking_type_id')
    def get_is_wholesale(self):
        for rec in self:
            rec.is_wholesale = False
            if rec.picking_type_id and rec.picking_type_id.operation_type == 'wholesale':
                rec.is_wholesale = True

    def action_view_orders(self):
        orders = self.env['container.order'].search([('parent_id', '=', self.id)])
        action = self.env.ref('taqat_donation.action_taqat_container_order_view').sudo().read()[0]
        action['domain'] = [('id', 'in', orders.ids)]
        return action

    def get_order_count(self):
        for rec in self:
            rec.order_count = len(self.sudo().search([('parent_id', '=', rec.id)]).ids)

    def action_order_confirm(self):
        for rec in self:
            if rec.total_weight <= 0:
                raise UserError(_("Total Weight must be greater than 0."))
            count = sum(rec.order_lines.mapped('nbr_of_bags'))
            if rec.total_weight < count:
                raise UserError(_("Total Weight must be Greater."))
            w_product_id = self.env.ref('taqat_donation.product_container_wholesale')
            s_product_id = self.env.ref('taqat_donation.product_container_scrap')
            c_product_id = self.env.ref('taqat_donation.product_container_generic')
            if not w_product_id:
                raise UserError(_("Wholesale Product not found."))
            if not s_product_id:
                raise UserError(_("Scrap Product not found."))
            if not c_product_id:
                raise UserError(_("Generic Product not found."))
            if rec.order_lines and rec.total_weight > count:
                rec.sudo().write({'order_lines': [(0, 0, {
                    'container_id': rec.order_lines.mapped('container_id')[0].id,
                    'nbr_of_bags': (rec.total_weight - count),
                    'operation_type': 'scrap',
                })]})
            if rec.parent_id:
                # if type is inspection
                if rec.picking_type_id and rec.picking_type_id.operation_type == 'inspection':
                    for lines in rec.order_lines:
                        if lines.operation_type and lines.operation_type == 'wholesale':
                            transfer = self.env['stock.picking'].sudo().create({
                                'origin': rec.container_id.name if rec.container_id else '',
                                'partner_id': rec.driver_id.id if rec.driver_id else False,
                                'picking_type_id': rec.parent_id.picking_type_id.id if rec.parent_id.picking_type_id else False,
                                'scheduled_date': datetime.datetime.today(),
                                'date_done': datetime.datetime.today(),
                                'location_dest_id': rec.picking_type_id.default_location_dest_id.id if rec.picking_type_id else False,
                                'location_id': rec.driver_id.property_stock_supplier.id,
                                'donation_order_id': rec.order_number.id if rec.order_number else False,
                                'container_order_id': rec.id,
                                'is_open_get_donation_product': False,
                            })
                            for line in rec.order_lines:
                                if line.operation_type and line.operation_type == 'wholesale' or line.operation_type == 'scrap':
                                    product_id = False
                                    if line.operation_type == 'wholesale':
                                        product_id = w_product_id
                                    elif line.operation_type == 'scrap':
                                        product_id = s_product_id
                                    if line.operation_type == 'wholesale' or line.operation_type == 'scrap':
                                        transfer.sudo().write({
                                            'move_ids_without_package': [(0, 0, {
                                                'product_id': product_id.product_variant_id.id if product_id.product_variant_id else False,
                                                'product_uom_qty': line.nbr_of_bags,
                                                'description_picking': line.comments,
                                                'name': line.comments if line.comments else ' ',
                                                'product_uom': product_id.uom_id.id if product_id.uom_id else False,
                                                'location_id': rec.driver_id.property_stock_supplier.id,
                                                'location_dest_id': rec.picking_type_id.default_location_dest_id.id if rec.picking_type_id else False,
                                            })]
                                        })
                            transfer.action_confirm()
                            transfer.button_validate()
                            wiz_obj = self.env['stock.immediate.transfer'].create({
                                'pick_ids': [transfer.id],
                                'show_transfers': False,
                                'immediate_transfer_line_ids': [[0, False, {
                                    'picking_id': transfer.id,
                                    'to_immediate': True
                                }]]
                            })
                            wiz_obj.with_context(button_validate_picking_ids=wiz_obj.pick_ids.ids).process()
                        if lines.operation_type and lines.operation_type == 'generic':
                            transfer = self.env['stock.picking'].sudo().create({
                                'origin': rec.container_id.name if rec.container_id else '',
                                'partner_id': rec.driver_id.id if rec.driver_id else False,
                                'picking_type_id': rec.parent_id.picking_type_id.id if rec.parent_id.picking_type_id else False,
                                'scheduled_date': datetime.datetime.today(),
                                'date_done': datetime.datetime.today(),
                                'location_dest_id': rec.picking_type_id.default_location_dest_id.id if rec.picking_type_id else False,
                                'location_id': rec.driver_id.property_stock_supplier.id,
                                'donation_order_id': rec.order_number.id if rec.order_number else False,
                                'container_order_id': rec.id,
                                'is_open_get_donation_product': True,
                            })
                            for line in rec.order_lines:
                                if line.operation_type and line.operation_type == 'generic':
                                    product_id = False
                                    if line.operation_type == 'generic':
                                        product_id = c_product_id
                                    transfer.sudo().write({
                                        'move_ids_without_package': [(0, 0, {
                                            'product_id': product_id.product_variant_id.id if product_id.product_variant_id else False,
                                            'product_uom_qty': line.nbr_of_bags,
                                            'description_picking': line.comments,
                                            'name': line.comments if line.comments else ' ',
                                            'product_uom': product_id.uom_id.id if product_id.uom_id else False,
                                            'location_id': rec.driver_id.property_stock_supplier.id,
                                            'location_dest_id': rec.picking_type_id.default_location_dest_id.id if rec.picking_type_id else False,
                                        })]
                                    })
                rec.state = 'confirm'
            else:
                for line in rec.order_lines:
                    if line.operation_type and line.operation_type == 'wholesale':
                        if sum(rec.order_lines.filtered(lambda x : x.operation_type != 'scrap').mapped('nbr_of_bags')) <= 0:
                            raise UserError(_('Please enter Quantity.'))
                        transfer = self.env['stock.picking'].sudo().create({
                            'origin': rec.container_id.name if rec.container_id else '',
                            'partner_id': rec.driver_id.id if rec.driver_id else False,
                            'picking_type_id': rec.picking_type_id.id if rec.picking_type_id else False,
                            'scheduled_date': datetime.datetime.today(),
                            'date_done': datetime.datetime.today(),
                            'location_dest_id': rec.picking_type_id.default_location_dest_id.id if rec.picking_type_id else False,
                            'location_id': rec.driver_id.property_stock_supplier.id,
                            'donation_order_id': rec.order_number.id if rec.order_number else False,
                            'container_order_id': rec.id,
                            'is_open_get_donation_product': False,
                        })
                        for line in rec.order_lines:
                            if line.operation_type and line.operation_type == 'wholesale' or line.operation_type == 'scrap':
                                product_id = False
                                if line.operation_type == 'wholesale':
                                    product_id = w_product_id
                                elif line.operation_type == 'scrap':
                                    product_id = s_product_id
                                if line.operation_type == 'wholesale' or line.operation_type == 'scrap':
                                    transfer.sudo().write({
                                        'move_ids_without_package': [(0, 0, {
                                            'product_id': product_id.product_variant_id.id if product_id.product_variant_id else False,
                                            'product_uom_qty': line.nbr_of_bags,
                                            'description_picking': line.comments,
                                            'name': line.comments if line.comments else ' ',
                                            'product_uom': product_id.uom_id.id if product_id.uom_id else False,
                                            'location_id': rec.driver_id.property_stock_supplier.id,
                                            'location_dest_id': rec.picking_type_id.default_location_dest_id.id if rec.picking_type_id else False,
                                        })]
                                    })
                        transfer.action_confirm()
                        transfer.button_validate()
                        wiz_obj = self.env['stock.immediate.transfer'].create({
                            'pick_ids': [transfer.id],
                            'show_transfers': False,
                            'immediate_transfer_line_ids': [[0, False, {
                                'picking_id': transfer.id,
                                'to_immediate': True
                            }]]
                        })
                        wiz_obj.with_context(button_validate_picking_ids=wiz_obj.pick_ids.ids).process()
                    elif line.operation_type and line.operation_type == 'inspection':
                        picking_type_id = self.env['stock.picking.type'].search(
                            [('operation_type', '=', line.operation_type)], limit=1)
                        if sum(rec.order_lines.filtered(lambda x : x.operation_type != 'scrap').mapped('nbr_of_bags')) <= 0:
                            raise UserError(_('Please enter Quantity.'))
                        if not picking_type_id:
                            raise UserError(_('Please create operation type of %s.' %(line.operation_type)))
                        if line.nbr_of_bags > 0:
                            self.env['container.order'].sudo().create({
                                'container_id': rec.container_id.id if rec.container_id else False,
                                'order_number': rec.order_number.id,
                                'driver_id': rec.driver_id.id if rec.driver_id else False,
                                'owner_id': rec.inspection_user_id.id if rec.inspection_user_id else False,
                                'is_created_by_donation': True,
                                'inspection_user_id': rec.inspection_user_id.id if rec.inspection_user_id else False,
                                'date': rec.date,
                                'parent_id': rec.id,
                                'picking_type_id': picking_type_id.id if picking_type_id else False,
                                'total_weight': line.nbr_of_bags,
                                'order_lines': [(0, 0, {
                                    'container_id': line.container_id.id,
                                    'nbr_of_bags': 0,
                                    'comments': line.comments,
                                    'operation_type': 'wholesale',
                                }), (0, 0, {
                                    'container_id': line.container_id.id,
                                    'nbr_of_bags': 0,
                                    'comments': line.comments,
                                    'operation_type': 'generic',
                                })],
                            })
                        rec.state = 'confirm'

    def action_order_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'


class ContainerOrderLines(models.Model):
    _name = 'container.order.line'

    container_id = fields.Many2one("donation.containers", "Containers")
    nbr_of_bags = fields.Float("weight")
    comments = fields.Char("Comments")
    container_order_id = fields.Many2one('container.order')
    operation_type = fields.Selection([('wholesale', 'Wholesale'), ('inspection', 'Inspection'), ('scrap', 'Scrap'), ('generic', 'Generic')],
                                      string="Operation Type")
