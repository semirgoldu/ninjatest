from odoo import models, fields, api, _


class PurchaseorderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, supplier, po):
        res = super(PurchaseorderLine, self)._prepare_purchase_order_line(product_id, product_qty, product_uom,
                                                                          company_id, supplier, po)
        if 'unit_price' in self._context:
            res['price_unit'] = self._context.get('unit_price')

        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    partner_id = fields.Many2one('res.partner', string='Vendor', required=False, states=READONLY_STATES,
                                 change_default=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count')
    is_procurement_manager = fields.Boolean(string="Is created by PM?", store=True, copy=False)

    @api.model
    def create(self, vals):
        if self.env.user and self.env.user.has_group('taqat_approval_extended.group_procurement_manager'):
            vals.update({'is_procurement_manager': True})
        else:
            vals.update({'is_procurement_manager': False})
        res = super(PurchaseOrder, self).create(vals)
        return res

    def _compute_approval_count(self):
        approval = self.env['approval.request']
        for rec in self:
            rec.approval_count = approval.search_count([('product_line_ids.purchase_order_line_id.order_id', '=', self.id)]) or 0

    project_id = fields.Many2one('project.project', string="Project")
    payment_state = fields.Char(string="Payment Status", compute='_compute_payment_state')


    def get_procurment_approval(self):
        return self.env['approval.request'].search([('product_line_ids.purchase_order_line_id', 'in', self.order_line.ids)])

    def get_purchase_approval(self):
        action = self.env["ir.actions.actions"]._for_xml_id("approvals.approval_request_action_all")
        tree_view = [(self.env.ref('approvals.approval_request_view_tree').id, 'tree')]
        action['views'] = tree_view + [(state, view) for state, view in action['views'] if view != 'tree']
        action['domain'] = [('product_line_ids.purchase_order_line_id.order_id', '=', self.id)]
        action['context'] = {}
        return action

    @api.depends('invoice_count')
    def _compute_payment_state(self):
        for rec in self:
            if rec.invoice_count > 0:
                value = ''
                for invoice in rec.invoice_ids:
                    value += str(invoice.name) + " - " + str(invoice.payment_state) + ", "
                rec.payment_state = value
            else:
                rec.payment_state = ''

    def is_accounting_manager(self):
        for rec in self:
            if rec.env.user.has_group('taqat_groups_access_rights_extended.taqat_group_accounting_manager_role'):
                return True
            else:
                return False

    def get_signature(self, name):
        for rec in self:
            user = self.env['res.users'].sudo().search([('name', '=like', name)])
            return user
