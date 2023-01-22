import logging

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import pager as portal_pager

_logger = logging.getLogger(__name__)


class MatagerCustomerPortal(CustomerPortal):
    # Added fields to save data on backend of my profile on confirm button.
    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id", "dob", "gender"]

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        # Redirect Url to my profile if verification is not done.
        if not request.env.user.is_phone_verify and not request.env.user.is_email_verify:
            return request.redirect('/my/account')
        else:
            return super(MatagerCustomerPortal, self).home(**kw)

    def _prepare_portal_layout_values(self):
        # Add data to portal.
        res = super(MatagerCustomerPortal, self)._prepare_portal_layout_values()
        res.update({
            'dob': request.env.user.partner_id.dob,
            'gender': request.env.user.partner_id.gender,
            'is_phone_verify': request.env.user.partner_id.is_phone_verify,
            'is_email_verify': request.env.user.partner_id.is_email_verify,
        })
        return res

    # Custom Request 
    def _prepare_home_portal_values(self, counters):
        # add data number of custom request of current user in my account.
        values = super(MatagerCustomerPortal, self)._prepare_home_portal_values(counters)
        custom_partner_ids = request.env['custom.request'].search([('user_id', '=', request.uid)])
        custom_partner_len = len(custom_partner_ids)
        values['custom_partner_len'] = custom_partner_len
        return values

    @http.route(['/custom/request', '/custom/request/page/<int:page>'], type='http', auth='public', website=True)
    def portal_my_custom_request(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        # set data for custom request
        values = self._prepare_portal_layout_values()
        custom_request = request.env['custom.request']

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'partner_id'},
        }

        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']

        # count for pager
        partner_id_count = custom_request.search_count([('user_id', '=', request.uid)])
        # pager
        pager = portal_pager(
            url="/custom/request",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=partner_id_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        custom_request_id = custom_request.search([('user_id', '=', request.uid)], order=order,
                                                  limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'custom_request_id': custom_request_id,
            'page_name': 'custom',
            'pager': pager,
            'default_url': '/custom/request',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'custom': True
        })
        return request.render("matager_account_modifier.custom_request_portal_sidebar_template", values)

    @http.route(['/custom/request/<int:id>'], type='http', auth="public", website=True)
    def portal_custom_page(self, id, access_token=None, **kw):
        # get id of selected record to show the data of that recode in new page
        custom_request = self._document_check_access('custom.request', id, access_token=access_token)
        values = {
            'custom_request': custom_request,
        }
        return request.render("matager_account_modifier.custom_request_portal_template", values)

    def details_form_validate(self, data):
        # super call method for adding phone validation error
        error, error_msg = super(MatagerCustomerPortal, self).details_form_validate(data)
        # Phone validation
        if data.get('phone') and len(data.get('phone')) > 8 or len(data.get('phone')) < 8:
            error["phone"] = 'error'
            error_msg.append(_('Invalid phone! Please enter a valid Phone Number.'))
        return error, error_msg