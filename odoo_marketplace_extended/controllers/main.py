from odoo.addons.web.controllers.main import ensure_db
from odoo import http
from odoo.http import request
from odoo.addons.odoo_marketplace.controllers.main import Home
from odoo.addons.portal.controllers.web import Home as portalHome
from odoo.addons.odoo_marketplace.controllers.main import AuthSignupHome
from odoo.addons.odoo_marketplace.controllers.main import website_marketplace_dashboard
import logging
import werkzeug

_logger = logging.getLogger(__name__)


class PortalHomeExtended(portalHome):
    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        # if not request.env.user.is_phone_verify and not request.env.user.is_email_verify and not request.env.user.has_group('base.group_user'):
        # if request.params and dict(request.params) and 'login' in dict(request.params):
        #     if request.httprequest and request.httprequest.path and request.httprequest.path == '/web/login':
        res = super(portalHome, self).web_client(s_action, **kw)
        if request.env.user and request.env.user.is_phone_verify == False and not request.env.user.has_group('base.group_system'):
            request.session.is_phone_otp = True
            return request.redirect('/web/signup/phone/verify?phone=%s' % (request.env.user.phone))
        elif request.env.user and request.env.user.is_email_verify == False and not request.env.user.has_group('base.group_system'):
            request.session.is_email_otp = True
            return request.redirect('/web/signup/email/verify?email=%s' % (request.env.user.email))
        else:
            return res


class Homeextended(Home):

    # @http.route('/web', type='http', auth="none")
    # def web_client(self, s_action=None, **kw):
    #     if request.session.uid and request.env.ref('odoo_marketplace_extended.group_seller_role') not in request.env['res.users'].sudo().browse(request.session.uid).role_line_ids.ids:
    #         return request.redirect_query('/my', query=request.params)
    #     return super(portalHome, self).web_client(s_action, **kw)
    # @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        # if request.session.uid:
        #     current_user = request.env['res.users'].sudo().browse(request.session.uid)
        #     if current_user.has_group('odoo_marketplace.marketplace_draft_seller_group') and current_user.partner_id.seller:
        #     # if not current_user.has_group('base.group_user') and current_user.has_group('odoo_marketplace.marketplace_draft_seller_group') and current_user.partner_id.seller:
        #         request.uid = request.session.uid
        #         try:
        #             context = request.env['ir.http'].webclient_rendering_context()
        #             response = request.render('web.webclient_bootstrap', qcontext=context)
        #             response.headers['X-Frame-Options'] = 'DENY'
        #             return response
        #         except AccessError:
        #             return werkzeug.utils.redirect('/web/login?error=access')
        return super(Home, self).web_client(s_action, **kw)


class AuthSignupHomeInherit(AuthSignupHome):

    @http.route()
    def web_login(self, redirect=None, *args, **kw):
        ensure_db()
        response = super(AuthSignupHome, self).web_login(redirect=redirect, *args, **kw)
        if request.params['login_success']:
            current_user = request.env['res.users'].browse(request.uid)
            if current_user.has_group('odoo_marketplace.marketplace_draft_seller_group') and current_user.partner_id.seller:
                seller_dashboard_menu_id = request.env['ir.model.data'].check_object_reference('odoo_marketplace', 'wk_seller_dashboard')[1]
                redirect = "/web#menu_id=" + str(seller_dashboard_menu_id)
                return request.redirect(redirect)
        return response


class website_marketplace_dashboard_inherit(website_marketplace_dashboard):

    @http.route('/my/marketplace/seller', type='http', auth="public", website=True)
    def submit_as_seller(self, **post):
        country_id = post.get('country_id', False)
        url_handler = post.get('url_handler', False)
        current_user = request.env.user

        if country_id and url_handler:
            current_user.partner_id.write({
                'country_id': int(country_id),
                'url_handler': url_handler,
                'seller': True,
            })
            # internal_group = request.env.ref('base.group_user')
            portal_group = request.env.ref('base.group_portal')
            seller_portal_group = request.env.ref('odoo_marketplace_extended.group_seller_role')
            if portal_group and seller_portal_group:
                # if portal_group and internal_group:
                #     portal_group.sudo().write({"users": [(3, current_user.id, 0)]})
                portal_group.sudo().write({"users": [(4, current_user.id, 0)]})
                seller_portal_group.sudo().write({"line_ids": [(0, 0, {'user_id': current_user.id})]})
                # internal_group.sudo().write({"users": [(4, current_user.id, 0)]})
            draft_seller_group_id = request.env['ir.model.data'].sudo().check_object_reference('odoo_marketplace', 'marketplace_draft_seller_group')[1]
            groups_obj = request.env["res.groups"].browse(draft_seller_group_id)
            if groups_obj:
                for group_obj in groups_obj:
                    group_obj.sudo().write({"users": [(4, current_user.id, 0)]})

        return request.redirect('/my/marketplace/become_seller')
