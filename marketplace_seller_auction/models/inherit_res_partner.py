# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    allow_seller_for_auction = fields.Boolean(
        string= 'Allow Seller to Make Product Auction',
        compute= "_get_auction_info_for_seller",
        )

    def _get_auction_info_for_seller(self):
        for obj in self:
            obj.allow_seller_for_auction = False
            seller_auction_group = self.env.ref('marketplace_seller_auction.group_for_mp_auction')
            user_obj = self.env["res.users"].sudo().search([('partner_id', '=', obj.id)])
            user_groups = user_obj.read(['groups_id'])
            if user_groups and user_groups[0].get("groups_id"):
                user_groups_ids = user_groups[0].get("groups_id")
                if seller_auction_group.id in user_groups_ids:
                    obj.allow_seller_for_auction = True
            else:
                obj.allow_seller_for_auction = False

    def enable_seller_auction_group(self):
        for obj in self:
            user = self.env["res.users"].sudo().search(
                [('partner_id', '=', obj.id)])
            if user:
                group = self.env.ref('marketplace_seller_auction.group_for_mp_auction')
                if group:
                    group.sudo().write({"users": [(4, user.id, 0)]})

    def disable_seller_auction_group(self):
        for obj in self:
            user = self.env["res.users"].sudo().search(
                [('partner_id', '=', obj.id)])
            if user:
                group = self.env.ref('marketplace_seller_auction.group_for_mp_auction')
                if group:
                    group.sudo().write({"users": [(3, user.id, 0)]})
