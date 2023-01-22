# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#	See LICENSE file for full copyright and licensing details.
#
##########################################################################

from odoo import api, fields, models
from odoo.addons.website_auction.models.website_auction import WkWebsiteAuction, name_list,notify_list
import logging
_logger = logging.getLogger(__name__)

class Website(models.Model):

	_inherit = "website"

	publish_total_bids = fields.Boolean(string='Total Bids',
								default= 1)
	publish_info_link = fields.Boolean(string='Auction Details Link',
								default= 1)
	publish_subscribe_link = fields.Boolean(string='Subscribe Link',
								model = 'wk.website.auction',
								default= 1)
	publish_start_date = fields.Boolean(string='Start Date',
								default= 1)
	publish_end_date = fields.Boolean(string='End Date',
								default= 1)
	publish_extend_date = fields.Boolean(string='Extend Date',
								default= 1)
	publish_intial_price = fields.Boolean(string='Initial Price',
								default= 1)
	publish_current_price = fields.Boolean(string='Current Price',
								default= 1)
	publish_simple_bid = fields.Boolean(string='Simple Bid Option',
								default= 1)
	publish_auto_bid = fields.Boolean(string='Auto Bid Option',
								default= 1)
	publish_next_bid = fields.Boolean(string='Next Bid Amount',
								default= 1)
	publish_user_highest_bid = fields.Boolean(string='User Highest Bid Amount',
								default= 1)
	publish_user_auto_bid = fields.Boolean(string='User Auto Bid Amount',
								default= 1)
	###################### Message for complete cancel close  ######
	publish_auction_complete = fields.Boolean(string='Auction Complete',
								default= 1)
	auction_complete_msz = fields.Text(string='Auction Complete Message',
								default= 'Auction has been Finished on this Product.',
								translate=True)
	auction_cancel_msz = fields.Text(string='Auction Cancel Message',
								default='Auction has been Canceled on this Product.', translate=True)
	publish_auction_close = fields.Boolean(string='Auction Close',
								default= 1)
	auction_close_msz = fields.Text(string='Auction Close Message', translate=True,
								default= 'Auction has been Closed on this Product.')

	publish_login_first = fields.Boolean(string='Login First',
								default=1)
	publish_login_first_msz = fields.Text(string='Login In First Message',
								default= 'Please Login First.',
								translate=True)
	auction_bid_submitted = fields.Boolean(string='Bid Placed',
								default= 1)
	auction_bid_submitted_msz = fields.Text(string='Auction Bid Submitted Message',
								default= 'You bid had been successfully submitted.',
								translate=True)
	publish_unexpected_error = fields.Boolean(string='Unexpected Error',
								default= 1)
	publish_unexpected_error_msz = fields.Text(string='Unexpected Error Message',
								default= 'Something Wrong happen ,Please Try again.',
								translate=True)

	publish_min_bid_error = fields.Boolean(string='Minimum Bid Error',
								default= 1)
	publish_min_bid_error_msz = fields.Text(string='Minimum Bid Error Message',
								default= 'Bid Amount is less than next minimum acceptable bid amount.',
								translate=True)

	publish_min_autobid_error = fields.Boolean(string='Minimum Auto Bid Error',
								default= 1)
	publish_min_autobid_error_msz = fields.Text(string='Min AutoBid Error Message', translate=True,
								default= 'Auto Bid Amount is less than Next Minimum Acceptable Auto Bid Amount. Please make higher Amount of Auto Bid.')

	publish_bid_subscribe = fields.Boolean(string='Subscribed Message',
								default=1)

	publish_bid_subscribe_msz = fields.Text(string='Subscribe Message', translate=True,
								default= 'Notification For Auction Subscribed.')


	publish_bid_unsubscribe = fields.Boolean(string='Un-Subscribed Message',
								default= 1)

	publish_bid_unsubscribe_msz = fields.Text(string='Un-Subscribe Message', translate=True,
								default='Notification For Auction Un-Subscribed.')




	#################### Bidder Info  ############################
	publish_bidders_name=fields.Selection(selection=name_list, translate=True,
								string = "Bidders ",
								default= 'cross')

	publish_bid_record = fields.Integer(string='Publish Bid Records',
										default= 10,
										required=1)

	###################### Winner Info  ##########################
	publish_winner_name=fields.Selection(selection=name_list,
								string = "Winner ",
								default= 'cross',
								translate=True)
