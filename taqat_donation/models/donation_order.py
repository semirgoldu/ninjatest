from odoo import models, fields, api, _
from odoo.exceptions import  UserError
from lxml import etree
from itertools import accumulate



class DonationOrder(models.Model):
    _name = 'donation.order'
    _rec_name = 'order_number'

    order_number = fields.Char("Order Number", required=True, readonly=True, default=lambda self: _('New'), copy=False)
    order_date = fields.Datetime("Order Date", default=fields.Date.today)
    driver_id = fields.Many2one("res.partner", "Driver", domain=[('is_driver', '=', True)])
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.uid)
    is_driver = fields.Boolean(default=False, copy=False, compute="get_is_driver")
    donator_id = fields.Many2one("res.partner", "Donator")
    mobile_no = fields.Char("Mobile", related='donator_id.mobile',store=True)
    zone = fields.Char("Zone")
    street = fields.Char("Street")
    description = fields.Char("Description")
    building_no = fields.Char("Building No")
    donation_type = fields.Many2one("donation.type", "Donation Type")
    is_container = fields.Boolean("Container", related='donation_type.is_container')
    attachment_number = fields.Integer('Number of Attachments', compute='_donation_compute_attachment_number')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('received', 'Received'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ], default='draft', string="State")
    donation_order_line_ids = fields.One2many('donation.order.line',
                                              'donation_order_id')
    donation_order_containers_ids = fields.One2many('donation.order.containers',
                                                    'donation_order_id')

    is_generate_receipt = fields.Boolean("Is Generate Receipt",copy=False)
    show_generate_receipt = fields.Boolean(copy=False, compute="get_show_generate_receipt")
    sign_signature = fields.Binary(string="Digital Signature")

    def get_signature(self, user):
        for rec in self:
            user = self.env['res.users'].sudo().search([('partner_id', '=', user.id)])
            return user

    def get_show_generate_receipt(self):
        for rec in self:
            rec.show_generate_receipt = True
            picking_ids = self.env['stock.picking'].sudo().search([('donation_order_id', '=', rec.id), ('state', 'not in', ['cancel'])])
            container_ids = self.env['container.order'].sudo().search([('order_number', '=', rec.id), ('state', 'not in', ['cancel'])])
            if rec.is_container and container_ids:
                rec.show_generate_receipt = False
            if picking_ids and not rec.is_container:
                rec.show_generate_receipt = False

    def get_is_driver(self):
        for rec in self:
            rec.is_driver = False
            if self.env.user.has_group('taqat_donation.group_driver'):
                if not self.env.user.has_group('taqat_donation.group_donation_manager') or not self.env.user.has_group('taqat_groups_access_rights_extended.taqat_group_inventory_manager_role'):
                    rec.is_driver = True

    def button_approve(self):
        self.state = 'approved'
        if not self.driver_id:
            raise UserError(_("Please enter driver first."))
        if self.donation_type and self.donation_type.is_container:
            product_ids = self.env['product.template'].sudo().search([('is_wholesale', '=', True)])
            picking_type_ids = self.env['stock.picking.type'].sudo().search([('is_container_type', '=', True)])
            if not product_ids:
                raise UserError(_("Please create product first."))
            if not picking_type_ids:
                raise UserError(_("Please create operation type for container."))
            for container in self.donation_order_containers_ids:
                if int(container.nbr_of_bags) <= 0:
                    raise UserError(_("Please enter Quantity."))

    @api.model
    def create(self, vals):
        if not vals.get('order_number') or vals['order_number'] == _('New'):
            vals['order_number'] = self.env.ref('taqat_donation.sequence_donation_order_sequence').next_by_code(sequence_code="donation.order") or _('New')
        res = super(DonationOrder, self).create(vals)
        return res

    def button_receive(self):
        self.state = 'received'

    def button_complete(self):
        if self.attachment_number >=1:
            self.state = 'delivered'
        else:
            raise UserError(_("Please add attachment."))

    def button_cancel(self):
        self.state = 'canceled'

    def button_reset_to_draft(self):
        self.state = 'draft'

    def button_print_slip(self):
        return self.env.ref('taqat_donation.taqat_donation_report').report_action(self)

    def _donation_compute_attachment_number(self):
        domain = [('res_model', '=', 'donation.order'), ('res_id', 'in', self.ids)]
        attachment_data = self.env['ir.attachment'].read_group(domain, ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for request in self:
            request.attachment_number = attachment.get(request.id, 0)

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'donation.order'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'donation.order', 'default_res_id': self.id}
        return res

    def action_get_donation_transfer_view(self):
        self.ensure_one()
        res = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        res['domain'] = [('donation_order_id', 'in', self.ids)]
        res['context'] = {'donation_order_id': self.id}
        return res

    def action_get_container_view(self):
        self.ensure_one()
        res = self.env["ir.actions.actions"]._for_xml_id("taqat_donation.action_taqat_container_order_view")
        res['domain'] = [('order_number', 'in', self.ids), ('parent_id', '=', False)]
        res['context'] = {'donation_order_id': self.id}
        return res

    def get_web_cam_image(self, **kw):
        print("selffffffffffff",self, kw)
        attachment_data = {
            'name': self.order_number,
            'datas': kw.get('image'),
            'res_model': kw.get('model'),
            'res_id': self.id
        }
        self.env['ir.attachment'].create(attachment_data)
        # self.env['ir.attachment'].create

    @api.constrains('donation_order_containers_ids', 'donation_order_containers_ids.container_id')
    def check_container_type(self):
        for rec in self:
            if len(rec.donation_order_containers_ids) > 1:
                raise UserError(_("Please add only one container."))

    def button_generate_slip(self):
        picking = self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1)
        if self.is_container == True:
            container_picking_id = self.env['stock.picking.type'].sudo().search([('is_container_type', '=', True)], limit=1)
            if not container_picking_id:
                raise UserError(_("Please create operation type for container."))
            for container in self.donation_order_containers_ids:
                vals = {
                    'container_id': container.container_id.id if container.container_id else False,
                    'order_number': self.id,
                    'driver_id': self.driver_id.id if self.driver_id else False,
                    'owner_id': self.env.user.id if self.env.user else False,
                    'is_created_by_donation': True,
                    'date': self.order_date.date(),
                    'picking_type_id': container_picking_id.id if container_picking_id else False,
                    'total_weight': container.nbr_of_bags,
                    'order_lines': [(0, 0, {
                        'container_id': container.container_id.id,
                        'nbr_of_bags': 0,
                        'comments': container.comments,
                        'operation_type': 'wholesale',
                        }), (0, 0, {
                        'container_id': container.container_id.id,
                        'nbr_of_bags': 0,
                        'comments': container.comments,
                        'operation_type': 'inspection',
                        })]
                }
                self.env['container.order'].sudo().create(vals)
            # self.env['stock.picking'].sudo().create({'origin': self.order_number,
            #                                          'partner_id': self.driver_id.id,
            #                                          'picking_type_id': picking.id,
            #                                          'scheduled_date': self.order_date,
            #                                          'location_dest_id': picking.default_location_dest_id.id,
            #                                          'location_id': self.driver_id.property_stock_supplier.id,
            #                                          'donation_order_id': self.id,
            #                                          'move_ids_without_package': [(0, 0, {
            #                                              'product_id': self.env.ref(
            #                                                  'taqat_donation.product_container').id,
            #                                              'product_uom_qty': container.nbr_of_bags,
            #                                              'description_picking': container.comments,
            #                                              'name': container.comments,
            #                                              'product_uom': self.env.ref(
            #                                                  'taqat_donation.product_container').uom_id.id,
            #                                              'location_id': container.donation_order_id.driver_id.property_stock_supplier.id,
            #                                              'location_dest_id': picking.default_location_dest_id.id,
            #                                          }) for container in self.donation_order_containers_ids]
            #                                          })
        else:
            data = self.env['stock.picking'].sudo().create({'origin': self.order_number,
                                                            'partner_id': self.driver_id.id,
                                                            'picking_type_id': picking.id,
                                                            'scheduled_date': self.order_date,
                                                            'location_dest_id': picking.default_location_dest_id.id,
                                                            'location_id': self.driver_id.property_stock_supplier.id,
                                                            'donation_order_id': self.id,
                                                            'move_ids_without_package': [(0, 0, {
                                                                'product_id': donation.product_id.product_variant_id.id,
                                                                'product_uom_qty': donation.quantity,
                                                                'description_picking': donation.description,
                                                                'name': donation.description,
                                                                'product_uom': donation.product_uom_id.id,
                                                                'location_id': donation.donation_order_id.driver_id.property_stock_supplier.id,
                                                                'location_dest_id': picking.default_location_dest_id.id,
                                                            }) for donation in self.donation_order_line_ids]
                                                            })
        self.is_generate_receipt = True

    def button_print_container_code(self):
        self.ensure_one()
        if not self.donation_order_containers_ids:
            raise UserError(_("Please Enter Container."))
        if int(self.donation_order_containers_ids[0].nbr_of_bags) <= 0:
            raise UserError(_("Please Enter Container Quantity."))
        return self.env.ref('taqat_donation.taqat_container_code_report').report_action(self)

    @api.model
    def get_formate_data(self):
        # if self:
        length_to_split = [2] * int(int(self.donation_order_containers_ids[0].nbr_of_bags) / 2) or []
        if int(self.donation_order_containers_ids[0].nbr_of_bags) % 2 != 0:
            length_to_split.append(1)
        total_list_len = [self.donation_order_containers_ids[0] for r in range(int(self.donation_order_containers_ids[0].nbr_of_bags))]
        data = [total_list_len[x - y: x] for x, y in zip(accumulate(length_to_split), length_to_split)]
        return data

class DonationOrderLine(models.Model):
    _name = 'donation.order.line'

    product_id = fields.Many2one("product.template", "product", domain=[('is_donation_generic', '=', True)])
    product_uom_id = fields.Many2one(comodel_name="uom.uom", string="UOM", related="product_id.uom_id")
    quantity = fields.Float("Quantity")
    description = fields.Char("Description")
    donation_order_id = fields.Many2one('donation.order')
    is_container = fields.Boolean("Container", related='donation_order_id.is_container')


class DonationOrderContainers(models.Model):
    _name = 'donation.order.containers'

    container_id = fields.Many2one("donation.containers", "Containers")
    nbr_of_bags = fields.Char("Number of bags")
    comments = fields.Char("Comments")
    donation_order_id = fields.Many2one('donation.order')
    is_container = fields.Boolean("Container", related='donation_order_id.is_container')

# class StockPickingInherit(models.Model):
#     _inherit = 'stock.picking'
#
#     donation_order_id = fields.Many2one("donation.order", 'Donation Order')
