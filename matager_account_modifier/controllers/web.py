import logging
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.web.controllers.main import Home
from odoo.addons.web.controllers import main

_logger = logging.getLogger(__name__)


class MatagerPhoneVerify(Home):

    # Reset Password route for Phone And Email
    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        context = self.get_auth_signup_qcontext()
        if 'login' in context and context.get('login'):
            context['phone'] = context.get('login')
            if request.env['res.users'].sudo().search([('login', '=', context.get('login'))]).id:
                return super(MatagerPhoneVerify, self).web_auth_reset_password(*args, **kw)
            else:
                user = request.env['res.users'].sudo().search([('phone', '=', kw.get('login'))])
                if not user:
                    context.update({'not_user_error': True})
                    return request.render('auth_signup.reset_password',context)
                request.session.is_phone_otp = True
                return request.redirect('/web/signup/phone/verify?is_reset_phone=True&phone_login=%s&phone=%s' % (context.get('login'),context.get('login')))
        else:
            return super(MatagerPhoneVerify, self).web_auth_reset_password(*args, **kw)

    # Redirect Login for signup if verification is not done for mobile or password
    def _login_redirect(self, uid, redirect=None):
        if not request.env.user.is_phone_verify and not request.env.user.is_email_verify and not request.env.user.has_group('base.group_user'):
            if request.params and dict(request.params) and 'login' in dict(request.params):
                if request.httprequest and request.httprequest.path and request.httprequest.path == '/web/login' or request.httprequest.path == '/seller/signup':
                    login_phone = request.env['res.users'].search([('phone','=',dict(request.params).get('login'))])
                    if login_phone:
                        request.session.is_phone_otp = True
                        redirect = '/web/signup/phone/verify?phone=%s'%(request.params.get('phone'))
                    else:
                        request.session.is_email_otp = True
                        redirect = '/web/signup/email/verify?email=%s'%(request.params.get('login'))
                else:
                    request.session.is_phone_otp = True
                    redirect = '/web/signup/phone/verify?phone=%s'%(request.params.get('phone'))
        elif request.env.user.has_group('base.group_user'):
            redirect ='/web'
            return main._get_login_redirect_url(uid, redirect)
        return main._get_login_redirect_url(uid, redirect)
