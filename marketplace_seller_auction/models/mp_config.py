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

from odoo import models,fields,api,_

class MarketplaceConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_allow_seller_for_auction = fields.Boolean(
        string= "Enable to allow Seller for Product Auctions",
        group= 'odoo_marketplace.marketplace_seller_group',
        implied_group= 'marketplace_seller_auction.group_for_mp_auction',
    )

    def set_values(self):
        super(MarketplaceConfigSettings, self).set_values()
        self.env['ir.default'].sudo().set('res.config.settings', 'group_allow_seller_for_auction', self.group_allow_seller_for_auction)
        return True

    @api.model
    def get_values(self, fields=None):
        res = super(MarketplaceConfigSettings, self).get_values()
        group_allow_seller_for_auction = self.env['ir.default'].sudo().get(
            'res.config.settings', 'group_allow_seller_for_auction')
        res.update({
            'group_allow_seller_for_auction':group_allow_seller_for_auction,
        })
        return res
