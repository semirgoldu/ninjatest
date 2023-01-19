from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    state = fields.Selection(selection_add=[('draft', 'Pending'),
        ('sent', 'Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')])



    def action_rejected(self):
        self.state = 'rejected'
        
    def button_approve(self, force=False):
        coo_approval_needed = False
        finance_approval_needed = False
        for line in self.order_line:
            if line.is_finanace_approval_needed and not finance_approval_needed:
                finance_approval_needed = True
            if line.is_coo_approval_needed and not coo_approval_needed:
                coo_approval_needed = True
        if (not coo_approval_needed and not finance_approval_needed) or force:
            return super(PurchaseOrder, self).button_approve(force=force)
        else:
            raise ValidationError(_("Please Approve the line first."))
        return {}
    
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()

            coo_approval_needed = False
            finance_approval_needed = False
            for line in self.order_line:
                if line.is_finanace_approval_needed and not finance_approval_needed:
                    finance_approval_needed = True
                if line.is_coo_approval_needed and not coo_approval_needed:
                    coo_approval_needed = True
            if not finance_approval_needed and not coo_approval_needed:
                order.button_approve(force=True)
            elif finance_approval_needed:
                raise ValidationError(_("Finanace Manager approval needed."))
            if not finance_approval_needed and coo_approval_needed:
                order.write({'state': 'to approve'})
            elif finance_approval_needed and coo_approval_needed:
                raise ValidationError(_("Finanace Manager approval needed."))
        return True
