# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
{
  "name"                 :  "Odoo Marketplace Seller Auction",
  "summary"              :  """Provides facility for Sellers of marketplace to enable bidding on their products.""",
  "category"             :  "website",
  "version"              :  "1.0.0",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Marketplace-Seller-Auction.html",
  "description"          :  """https://webkul.com/blog/odoo-marketplace-seller-auction/""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_seller_auction&lifetime=120&lout=0",
  "depends"              :  [
                             'odoo_marketplace',
                             'website_auction',
                            ],
  "data"                 :  [
                             'security/access_control_security.xml',
                             'security/ir.model.access.csv',
                             'data/mp_seller_auction_data.xml',
                             'views/inherit_website_auction.xml',
                             'views/mp_config_view.xml',
                             'views/mp_seller_view.xml',
                            ],
  "images"               :  ['static/description/Banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  45,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
