from odoo import api, fields, models, _
from odoo.addons.odoo_marketplace.models.res_users import ResUsers


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    def copy(self, default=None):
        self.ensure_one()
        if self._context.get('is_seller', False):
            user_role = self.env.ref('odoo_marketplace_extended.group_seller_role')
            default.update({
                'role_line_ids':[(0,0,{'role_id':user_role.id})],
            })
        user_obj = super(ResUsers, self).copy(default=default)
        website = self._context.get('website_id', False)
        if website:
            website = self.env["website"].browse(int(website))
        if self._context.get('is_seller', False):
            # Set Default fields for seller (i.e: payment_methods, commission, location_id, etc...)
            wk_valse = {
                "payment_method": [(6, 0, user_obj.partner_id._set_payment_method())],
                "commission": self.env['ir.default'].get('res.config.settings', 'mp_commission'),
                "location_id": self.env['ir.default'].get('res.config.settings', 'mp_location_id', company_id=True) or False,
                "warehouse_id": self.env['ir.default'].get('res.config.settings', 'mp_warehouse_id', company_id=True) or False,
                "auto_product_approve": self.env['ir.default'].get('res.config.settings', 'mp_auto_product_approve'),
                "seller_payment_limit": self.env['ir.default'].get('res.config.settings', 'mp_seller_payment_limit'),
                "next_payment_request": self.env['ir.default'].get('res.config.settings', 'mp_next_payment_request'),
                "auto_approve_qty": self.env['ir.default'].get('res.config.settings', 'mp_auto_approve_qty'),
                "seller" : True,
            }
            user_obj.partner_id.write(wk_valse)
            # Add user to Pending seller group
            draft_seller_group_id = self.env['ir.model.data'].check_object_reference('odoo_marketplace', 'marketplace_draft_seller_group')[1]
            groups_obj = self.env["res.groups"].browse(draft_seller_group_id)
            if groups_obj:
                for group_obj in groups_obj:
                    group_obj.write({"users": [(4, user_obj.id, 0)]})
        return user_obj
