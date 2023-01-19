from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    approval_id = fields.Many2one("approval.request")
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count')

    def _compute_approval_count(self):
        for rec in self:
            rec.approval_count = len(self.approval_id.ids)

    def get_purchase_approval(self):
        action = self.env["ir.actions.actions"]._for_xml_id("approvals.approval_request_action_all")
        tree_view = [(self.env.ref('approvals.approval_request_view_tree').id, 'tree')]
        action['views'] = tree_view + [(state, view) for state, view in action['views'] if view != 'tree']
        action['domain'] = [('id', '=', self.approval_id.id)]
        action['context'] = {}
        return action


class PurchaseRequisitionInherit(models.Model):
    _inherit = 'purchase.requisition'

    approval_id = fields.Many2one("approval.request")
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count')

    def _compute_approval_count(self):
        for rec in self:
            rec.approval_count = len(self.approval_id.ids)

    def get_purchase_approval(self):
        action = self.env["ir.actions.actions"]._for_xml_id("approvals.approval_request_action_all")
        tree_view = [(self.env.ref('approvals.approval_request_view_tree').id, 'tree')]
        action['views'] = tree_view + [(state, view) for state, view in action['views'] if view != 'tree']
        action['domain'] = [('id', '=', self.approval_id.id)]
        action['context'] = {}
        return action


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    project_id = fields.Many2one('project.project', string="Project")
    is_procurement_manager = fields.Boolean(string='Procurement Manager',compute='get_default_users')
    uniq_name = fields.Char(string="Name", readonly=True, required=True, copy=False, default='New')
    subject = fields.Char(string="Subject", copy=False)
    purchase_agreement_count = fields.Integer(compute='_compute_purchase_agreement_count')
    vendor_id = fields.Many2one('res.partner', string="Vendor")
    purchase_bill_count = fields.Integer(compute='_compute_purchase_bill_count')

    @api.depends('product_line_ids.purchase_order_line_id')
    def _compute_purchase_order_count(self):
        for request in self:
            purchases = request.product_line_ids.sudo().purchase_order_line_id.order_id
            request.purchase_order_count = len(purchases)

    def _compute_purchase_bill_count(self):
        for rec in self:
            bills = self.env['account.move'].sudo().search([('approval_id', '=', rec.id)]).ids
            rec.purchase_bill_count = len(bills)

    def _compute_purchase_agreement_count(self):
        for rec in self:
            purchases = self.env['purchase.requisition'].sudo().search([('approval_id', '=', rec.id)]).ids
            rec.purchase_agreement_count = len(purchases)

    def get_default_users(self):
        is_procurement_manager = False
        if self.env.user.has_group('taqat_approval_extended.group_procurement_manager'):
            is_procurement_manager = True
        self.is_procurement_manager = is_procurement_manager

    def action_approve(self,approver=None):
        if self.is_procurement_manager == True and any(self.product_line_ids.filtered(lambda x: not x.product_id)):
            raise UserError('Please Insert Product')
        else:
            return super(ApprovalRequest, self).action_approve(approver=approver)

    def action_confirm(self):
        if self.is_procurement_manager == True and any(self.product_line_ids.filtered(lambda x: not x.product_id)):
            raise UserError('Please Insert Product')
        else:
            return super(ApprovalRequest, self).action_confirm()

    @api.model
    def create(self, vals):
        if vals.get('uniq_name', 'New') == 'New':
            vals['uniq_name'] = self.env['ir.sequence'].next_by_code(
                'approval.request') or 'New'
        result = super(ApprovalRequest, self).create(vals)
        return result


    def action_create_purchase_orders(self):
        """ Create and/or modifier Purchase Orders. """
        if any(self.product_line_ids.filtered(lambda x: not x.product_id)):
            raise UserError('Please Insert Product')
        else:
            self.ensure_one()
            # self.product_line_ids._check_products_vendor()
            data = True
            new_purchase_order = False
            for line in self.product_line_ids:
                seller = line._get_seller_id()
                vendor = seller.name
                po_domain = line._get_purchase_orders_domain(vendor)
                purchase_orders = self.env['purchase.order'].search(po_domain)

                # if purchase_orders:
                #     # Existing RFQ found: check if we must modify an existing
                #     # purchase order line or create a new one.
                #     purchase_line = self.env['purchase.order.line'].search([
                #         ('order_id', 'in', purchase_orders.ids),
                #         ('product_id', '=', line.product_id.id),
                #         ('product_uom', '=', line.product_id.uom_po_id.id),
                #     ], limit=1)
                #     purchase_order = self.env['purchase.order']
                #     if purchase_line:
                #         # Compatible po line found, only update the quantity.
                #         line.purchase_order_line_id = purchase_line.id
                #         purchase_line.product_qty += line.po_uom_qty
                #         purchase_order = purchase_line.order_id
                #         purchase_line.price_unit = line.price_unit
                #     else:
                #         # No purchase order line found, create one.
                #         purchase_order = purchase_orders[0]
                #         po_line_vals = self.env['purchase.order.line'].with_context(unit_price=line.price_unit)._prepare_purchase_order_line(
                #             line.product_id,
                #             line.quantity,
                #             line.product_uom_id,
                #             line.company_id,
                #             seller,
                #             purchase_order,
                #         )
                #         po_line_vals.update({'name': line.description})
                #         new_po_line = self.env['purchase.order.line'].create(po_line_vals)
                #         line.purchase_order_line_id = new_po_line.id
                #         purchase_order.order_line = [(4, new_po_line.id)]
                #
                #     # Add the request name on the purchase order `origin` field.
                #     new_origin = set([self.name])
                #     if purchase_order.origin:
                #         missing_origin = new_origin - set(purchase_order.origin.split(', '))
                #         if missing_origin:
                #             purchase_order.write({'origin': purchase_order.origin + ', ' + ', '.join(missing_origin)})
                #     else:
                #         purchase_order.write({'origin': ', '.join(new_origin)})
                # else:
                # No RFQ found: create a new one.
                po_vals = line._get_purchase_order_values(vendor)
                if data:
                    new_purchase_order = self.env['purchase.order'].sudo().create(po_vals)
                    data = False
                po_line_vals = self.env['purchase.order.line'].sudo().with_context(
                    unit_price=line.price_unit)._prepare_purchase_order_line(
                    line.product_id,
                    line.quantity,
                    line.product_uom_id,
                    line.company_id,
                    seller,
                    new_purchase_order,
                )
                po_line_vals.update({'name': line.description})

                new_po_line = self.env['purchase.order.line'].sudo().create(po_line_vals)
                line.purchase_order_line_id = new_po_line.id
                new_purchase_order.order_line = [(4, new_po_line.id)]

    def action_open_purchase_agreement(self):
        """ Return the list of purchase Agreement the approval request created or
        affected in quantity. """
        self.ensure_one()
        domain = [('approval_id', '=', self.id)]
        action = {
            'name': _('Purchase Agreement'),
            'view_type': 'tree',
            'view_mode': 'list,form',
            'res_model': 'purchase.requisition',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'domain': domain,
        }
        return action

    def action_open_purchase_bill(self):
        """ Return the list of purchase Agreement the approval request created or
        affected in quantity. """
        self.ensure_one()
        domain = [('approval_id', '=', self.id)]
        action = {
            'name': _('Purchase Bill'),
            'view_type': 'tree',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'domain': domain,
        }
        return action

    def action_create_purchase_agreement(self):
        """ Create and/or modifier Purchase Agreement. """
        if any(self.product_line_ids.filtered(lambda x: not x.product_id)):
            raise UserError('Please Insert Product')
        else:
            self.ensure_one()
            purchase_agr_obj = self.env['purchase.requisition']
            vals = {
                'user_id': self.env.user.id,
                'approval_id': self.id,
                'ordering_date': self.date,
                'date_end': self.date_end,
            }
            new_pa = purchase_agr_obj.create(vals)
            for p_line in self.product_line_ids:
                new_pa.line_ids = [(0, 0, {
                    'product_id': p_line.product_id.id,
                    'product_qty': p_line.quantity,
                    'price_unit': p_line.price_unit,
                    'product_description_variants': p_line.description,
                })]

    def action_create_purchase_bill(self):
        """ Create and/or modifier Bill. """
        if any(self.product_line_ids.filtered(lambda x: not x.product_id)):
            raise UserError('Please Insert Product')
        elif not self.vendor_id:
            raise UserError('Please Enter vendor for create bill.')
        else:
            self.ensure_one()
            bill_obj = self.env['account.move']
            vals = {
                'partner_id': self.vendor_id.id if self.vendor_id else False,
                'approval_id': self.id,
                'move_type': 'in_invoice',
            }
            new_pa = bill_obj.create(vals)
            for p_line in self.product_line_ids:
                new_pa.invoice_line_ids = [(0, 0, {
                    'product_id': p_line.product_id.id,
                    'quantity': p_line.quantity,
                    'price_unit': p_line.price_unit,
                    'name': p_line.description,
                })]




class ApprovalProductLine(models.Model):
    _inherit = 'approval.product.line'

    price_unit = fields.Float("Unit Price")
