import logging
import datetime

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import SIGN_UP_REQUEST_PARAMS
from odoo.addons.website_sale.controllers.main import WebsiteSale

# Add signup Params
SIGN_UP_REQUEST_PARAMS.update(['phone', 'dob', 'gender', 'is_terms_condition_apply'])

_logger = logging.getLogger(__name__)

import math, random


# Generate Otp For Email
def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(4):
        OTP += digits[int(math.floor(random.random() * 10))]
    return OTP


class MatagerAuthSignupHome(AuthSignupHome):

    def _prepare_signup_values(self, qcontext):
        values = {key: qcontext.get(key) for key in
                  ('login', 'name', 'password', 'phone', 'dob', 'gender', 'is_terms_condition_apply')}
        # User error for same phone number
        if any(request.env["res.users"].sudo().search(
                [("phone", "=", values.get('phone'))])) and request.httprequest.path == '/web/signup':
            raise UserError(_('Another user is already registered using this phone number.'))
        if values.get('login') and not tools.single_email_re.match(values.get('login')):
            raise UserError(_('Invalid Email! Please enter a valid email address.'))
        if values.get('phone') and len(values.get('phone')) > 8 or len(values.get('phone')) < 8:
            raise UserError(_('Invalid phone! Please enter a valid phone number.'))
        # set data of signup page to User
        if 'phone' in values and values.get('phone'):
            values.update({'phone': int(values.get('phone'))})
        if 'dob' in values and values.get('dob'):
            values.update({'dob': datetime.datetime.strptime(values.get('dob'), '%Y-%m-%d')})
        if 'gender' in values and values.get('gender'):
            values.update({'gender': values.get('gender')})
        if 'is_terms_condition_apply' in values and values.get('is_terms_condition_apply'):
            values.update({'is_terms_condition_apply': values.get('is_terms_condition_apply')})
        if not values:
            raise UserError(_("The form was not properly filled in."))

        # comment UserError of confirm password in signup page
        # if values.get('password') != qcontext.get('confirm_password'):
        #     raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '')
        if lang in supported_lang_codes:
            values['lang'] = lang
        return values

    # check otp if already exist for phone
    def check_otp_phone(self, otp):
        if otp not in request.env.user.phone_otp_ids.mapped('otp'):
            request.env['otp.phonenumber'].sudo().create({
                'date': fields.datetime.now(),
                'otp': otp,
                'user_id': request.env.user.id,
            })
        else:
            otp = generateOTP()
            self.check_otp_phone(otp)
        request.env.user.phone_verification_code = otp
        return otp

    # check otp if already exist for email
    def check_otp_email(self, otp):
        if otp not in request.env.user.email_otp_ids.mapped('otp'):
            request.env['otp.email'].sudo().create({
                'date': fields.datetime.now(),
                'otp': otp,
                'user_id': request.env.user.id,
            })
        else:
            otp = generateOTP()
            self.check_otp_email(otp)
        request.env.user.email_verification_code = otp
        print("-------oooo",otp)
        return otp

    # otp send function
    def send_otp(self, number, shop_address=False):
        source_id = request.env['sms.connect.source'].sudo().search([('name', '=', 'OKSOUQ')])
        otp = generateOTP()
        if shop_address == False:
            otp = self.check_otp_phone(otp)
            print("------------", otp)
        else:
            request.session.shop_phone_otp_time = fields.Datetime.now()
            request.session.shop_phone_otp = otp
            print("------------",otp)
        sms_value = {
            'name': 'OTP',
            'ttype': 'number',
            'number': '974' + number,
            'date': fields.Datetime.now(),
            'content': '%s is the is the OTP to verify you phone number.OTP is confidential. We never call you asking for OTP. Please do not share it with anyone.' % (
                otp),
            'source': source_id.id if source_id else False
        }
        sms = request.env['sms.connect.sms'].sudo().create(sms_value)
        sms.send_sms()

    def send_email_otp(self, email=False, name=False, shop_address=False):
        otp = generateOTP()
        email_values = {
            'email_cc': False,
            'auto_delete': True,
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
        }
        if shop_address == False:
            otp = self.check_otp_email(otp)
            users = request.env.user
            template = request.env.ref('matager_account_modifier.mail_template_email_send_otp_verify')
            for user in users:
                if not user.email:
                    raise UserError(_("Cannot send email: user %s has no email address.", user.name))
                email_values['email_to'] = user.email
                template.sudo().send_mail(user.id, force_send=True, raise_exception=True, email_values=email_values)
        else:
            request.session.shop_email_otp = otp
            request.session.shop_email_otp_time = fields.Datetime.now()
            print("------------", otp)
            users = email
            email_values['email_to'] = users
            template = request.env.ref('matager_account_modifier.mail_template_shop_address_email_send_otp_verify')
            template.sudo().with_context(email=email, name=name, otp=otp).send_mail(res_id=request.env.user.id,
                                                                                    force_send=True,
                                                                                    raise_exception=True,
                                                                                    email_values=email_values)

    # Signup phone verification route
    @http.route('/web/phone/email/verify/url', type='http', auth='public', website=True, sitemap=False)
    def get_phone_email_verify_url(self, **kw):
        if 'my_profile_phone' in kw and kw.get('my_profile_phone') == 'True':
            request.session.is_phone_otp = True
            return request.redirect('/web/signup/phone/verify?phone=%s' %kw.get('phone'))
        if 'my_profile_email' in kw and kw.get('my_profile_email') == 'True':
            request.session.is_email_otp = True
            return request.redirect('/web/signup/email/verify?email=%s' % kw.get('email'))
        if 'is_reset_phone_otp' in kw and kw.get('is_reset_phone_otp') == 'True':
            request.session.is_phone_otp = True
            return request.redirect('/web/signup/phone/verify?is_reset_phone_otp=True&phone_login=%s&phone=%s' % (kw.get('phone_login'), kw.get('phone')))
        if 'is_reset_phone' in kw and kw.get('is_reset_phone') == 'True':
            request.session.is_phone_otp = True
            return request.redirect('/web/signup/phone/verify?is_reset_phone=True&phone_login=%s&phone=%s' % (kw.get('phone_login'), kw.get('phone')))
        if 'is_reset_email_otp' in kw and kw.get('is_reset_email_otp') == 'True':
            request.session.is_email_otp = True
            return request.redirect('/web/signup/email/verify?email=%s' %kw.get('email'))


    # Signup phone verification route
    @http.route('/web/signup/phone/verify', type='http', auth='public', website=True, sitemap=False)
    def get_signup_phone_verify(self, **kw):
        if request.session.is_phone_otp == True:
            request.session.is_phone_otp = False
            if 'is_reset_phone' in kw and 'phone_login' in kw:
                self.send_otp(kw.get('phone_login'))
                return request.render('matager_account_modifier.phone_number_verify_signup_template', kw)
            else:
                self.send_otp(kw.get('phone'))
                return request.render('matager_account_modifier.phone_number_verify_signup_template',{'phone':kw.get('phone')})

    # Phone Number change in shop address to show div
    @http.route('/web/shop/address/change/phone', type='json', auth='public', website=True, sitemap=False)
    def shop_address_change_phone_number(self, **kw):
        if kw.get('partner_id') and kw.get('partner_id') != '-1' and kw.get('change_phone'):
            if 'res.partner' in kw.get('partner_id'):
                partner = int(kw.get('partner_id').split('res.partner')[1].split(',')[0].split('(')[1])
            else:
                partner = int(kw.get('partner_id'))
            if request.env['res.partner'].sudo().browse(partner).phone == kw.get('change_phone'):
                return ({'show': False})
            else:
                if request.httprequest.headers.get_all('Referer')[0].split('/')[3].split('?')[0] == 'add-address':
                    temp = 'theme_vouge.phone_verification_template_vogue'
                else:
                    temp = 'matager_account_modifier.phone_verification_template'
                return ({'show': True, 'phone_render_template': request.env['ir.ui.view']._render_template(temp)})

        else:
            if kw.get('phone_verify_field') == kw.get('change_phone'):
                return ({'show': False})
            else:
                if request.httprequest.headers.get_all('Referer')[0].split('/')[3].split('?')[0] == 'add-address':
                    temp = 'theme_vouge.phone_verification_template_vogue'
                else:
                    temp = 'matager_account_modifier.phone_verification_template'
                return ({'show': True,'phone_render_template': request.env['ir.ui.view']._render_template(temp)})

    # Email change in shop address to show div
    @http.route('/web/shop/address/change/email', type='json', auth='public', website=True, sitemap=False)
    def shop_address_change_email_number(self, **kw):
        if kw.get('partner_id') and kw.get('partner_id') != '-1' and kw.get('change_email'):
            if 'res.partner' in kw.get('partner_id'):
                partner = int(kw.get('partner_id').split('res.partner')[1].split(',')[0].split('(')[1])
            else:
                partner = int(kw.get('partner_id'))
            if request.env['res.partner'].sudo().browse(partner).email == kw.get('change_email'):
                return ({'show': False})
            else:
                if request.httprequest.headers.get_all('Referer')[0].split('/')[3].split('?')[0] == 'add-address':
                    temp = 'theme_vouge.email_verification_template_vogue'
                else:
                    temp = 'matager_account_modifier.email_verification_template'
                return ({'show': True ,'email_render_template': request.env['ir.ui.view']._render_template(temp)})
        else:
            if kw.get('email_verify_field') == kw.get('change_email'):
                return ({'show': False})
            else:
                if request.httprequest.headers.get_all('Referer')[0].split('/')[3].split('?')[0] == 'add-address':
                    temp = 'theme_vouge.email_verification_template_vogue'
                else:
                    temp = 'matager_account_modifier.email_verification_template'
                return ({'show': True ,'email_render_template': request.env['ir.ui.view']._render_template(temp)})

    # Phone Number otp verify in shop address
    @http.route('/web/shop/address/phone/otp/verify/submit', type='json', auth='public', website=True, sitemap=False)
    def shop_address_phone_otp_verify_submit(self, **kw):
        phone_otp_date_time = request.session.shop_phone_otp_time
        datetime_now = fields.Datetime.now()
        difference_time = (datetime_now - phone_otp_date_time).total_seconds()/60
        if difference_time > request.env.user.company_id.resend_opt_time:
            return ({'phone_otp_expire': True})
        elif kw.get('phone_verify') != request.session.shop_phone_otp:
            return ({'phone_verify': False})
        else:
            return ({'phone_verify': True})

    # email otp verify in shop address
    @http.route('/web/shop/address/email/otp/verify/submit', type='json', auth='public', website=True, sitemap=False)
    def shop_address_email_otp_verify_submit(self, **kw):
        email_otp_date_time = request.session.shop_email_otp_time
        datetime_now = fields.Datetime.now()
        difference_time = (datetime_now - email_otp_date_time).total_seconds() / 60
        if difference_time > request.env.user.company_id.resend_opt_time:
            return ({'email_otp_expire': True})
        elif kw.get('email_verify') != request.session.shop_email_otp:
            return ({'email_verify': False})
        else:
            return ({'email_verify': True})

    # Phone Number send otp in shop address
    @http.route('/web/shop/address/phone/verify/send/otp', type='json', auth='public', website=True, sitemap=False)
    def get_shop_address_phone_verify_send_opt(self, **kw):
        if 'phone' in kw and not kw.get('phone') == '' and len(kw.get('phone')) == 8:
            user = request.env['res.users'].sudo().search(
                [('phone', '=', kw.get('phone')), ('id', '!=', request.env.user.id)])
            if kw.get('partner') == '-1' and request.env.user.id == request.env.ref('base.public_user').id:
                partner = request.env['res.partner'].sudo().search(
                    [('phone', '=', kw.get('phone')), ('phone', '!=', request.session.shop_phone)])
            elif request.env.user.id != request.env.ref('base.public_user').id:
                partner = request.env['res.partner'].sudo().search(
                    [('phone', '=', kw.get('phone')), ('id', '!=', request.env.user.partner_id.id),
                     ('parent_id', '!=', request.env.user.partner_id.parent_id.id)])
            else:
                partner_obj = request.env['res.partner'].sudo().browse(int(kw.get('partner')))
                partner = request.env['res.partner'].sudo().search(
                    [('email', '=', kw.get('email')), ('id', '!=', int(kw.get('partner'))),
                     ('parent_id', '!=', partner_obj.parent_id.id)])
            if user or partner:
                return ({'not_user_error': True})
            else:
                request.session.shop_phone = kw.get('phone')
                self.send_otp(kw.get('phone'), shop_address=True)
                return ({'not_user_error': False, 'timer': str(request.env.user.company_id.resend_opt_time)})
        elif not kw.get('phone') == '' and len(kw.get('phone')) != 8:
            return ({'in_correct_phone_number': True})
        else:
            return ({'not_phone': True})

    # Email send otp in shop address
    @http.route('/web/shop/address/email/verify/send/otp', type='json', auth='public', website=True, sitemap=False)
    def get_shop_address_email_verify_send_opt(self, **kw):
        if 'email' in kw and not kw.get('email') == '' and tools.single_email_re.match(kw.get('email')):
            user = request.env['res.users'].sudo().search([('email', '=', kw.get('email')),('id', '!=', request.env.user.id)])
            if kw.get('partner') == '-1' and request.env.user.id == request.env.ref('base.public_user').id:
                partner = request.env['res.partner'].sudo().search([('email', '=', kw.get('email')),('email', '!=', request.session.shop_email)])
            elif request.env.user.id != request.env.ref('base.public_user').id:
                partner = request.env['res.partner'].sudo().search([('email', '=', kw.get('email')), ('id', '!=',request.env.user.partner_id.id),('parent_id', '!=', request.env.user.partner_id.parent_id.id)])
            else:
                partner_obj = request.env['res.partner'].sudo().browse(int(kw.get('partner')))
                partner = request.env['res.partner'].sudo().search([('email', '=', kw.get('email')), ('id', '!=', int(kw.get('partner'))),('parent_id', '!=', partner_obj.parent_id.id)])
            if user or partner:
                return ({'not_user_error': True})
            else:
                request.session.shop_email = kw.get('email')
                self.send_email_otp(email=kw.get('email'), name=kw.get('name'), shop_address=True)
                return ({'not_user_error': False,'timer':str(request.env.user.company_id.resend_opt_time)})
        elif not kw.get('email') == '' and not tools.single_email_re.match(kw.get('email')):
            return ({'in_correct_email': True})
        else:
            return ({'not_email': True})

    # Phone Number otp verify in signup 
    @http.route('/web/signup/phone/verify/submit', type='http', auth='public', website=True, sitemap=False)
    def get_signup_phone_verify_submit(self, **kw):
        phone_otp_date_time = request.env.user.phone_otp_ids[-1].date
        datetime_now = fields.Datetime.now()
        difference_time = (datetime_now - phone_otp_date_time).total_seconds() / 60
        if difference_time > request.env.user.company_id.resend_opt_time:
            return request.render('matager_account_modifier.phone_number_verify_signup_template', {'otp_phone_expire_error': True, 'is_reset_phone': True, 'phone_login': kw.get('phone_login'),'phone': kw.get('phone')})
        elif 'phone_verify' in kw:
            if 'is_reset_phone' in kw and 'phone_login' in kw and kw.get('is_reset_phone') == '' and kw.get('phone_login') == '' and kw.get('phone_verify') == request.env.user.phone_verification_code:
                request.env.user.is_phone_verify = True
                if request.env.user.has_group('base.group_portal') and request.env.ref('odoo_marketplace_extended.group_seller_role') not in request.env.user.role_line_ids.mapped('role_id'):
                    return request.redirect('/my')
                else:
                    return request.redirect('/web')
            elif 'is_reset_phone' in kw and 'phone_login' in kw and kw.get('is_reset_phone') != '' and kw.get('phone_login') != '':
                if kw.get('phone_verify') == request.env.user.phone_verification_code:
                    user = request.env['res.users'].sudo().search([('phone', '=', kw.get('phone_login'))])
                    if not user:
                        return request.render('matager_account_modifier.phone_number_verify_signup_template',{'not_user_error': True, 'is_reset_phone': True,'phone_login': kw.get('phone_login'),'phone': kw.get('phone')})
                    user.partner_id.signup_prepare(signup_type="reset")
                    return request.redirect(user.signup_url)
                else:
                    return request.render('matager_account_modifier.phone_number_verify_signup_template',{'error': True, 'is_reset_phone': True, 'phone_login': kw.get('phone_login'),'phone': kw.get('phone')})
            else:
                return request.render('matager_account_modifier.phone_number_verify_signup_template',{'error': True, 'is_reset_phone': '', 'phone_login': '','phone': kw.get('phone')})
        else:
            return request.render('matager_account_modifier.phone_number_verify_signup_template',{'error': True, 'is_reset_phone': True, 'phone_login': kw.get('phone_login'),'phone': kw.get('phone')})

    # Signup Email verification route
    @http.route('/web/signup/email/verify', type='http', auth='public', website=True, sitemap=False)
    def get_signup_email_verify(self,**kw):
        if request.session.is_email_otp == True:
            request.session.is_email_otp = False
            self.send_email_otp(email=kw.get('email'), shop_address=False)
            return request.render('matager_account_modifier.email_verify_signup_template',{'email':kw.get('email')})

    # Submit Email verification route
    @http.route('/web/signup/email/verify/submit', type='http', auth='public', website=True, sitemap=False)
    def get_signup_email_verify_submit(self, **kw):
        email_otp_date_time = request.env.user.email_otp_ids[-1].date
        datetime_now = fields.Datetime.now()
        difference_time = (datetime_now - email_otp_date_time).total_seconds() / 60
        if difference_time > request.env.user.company_id.resend_opt_time:
            return request.render('matager_account_modifier.email_verify_signup_template', {'otp_email_expire_error': True,'email':kw.get('email')})
        elif 'email_verify' in kw and kw.get('email_verify') == request.env.user.email_verification_code:
            request.env.user.is_email_verify = True
            if request.env.user.has_group('base.group_portal') and request.env.ref('odoo_marketplace_extended.group_seller_role') not in request.env.user.role_line_ids.mapped('role_id'):
                return request.redirect('/my')
            else:
                return request.redirect('/web')
        else:
            return request.render('matager_account_modifier.email_verify_signup_template', {'error': True,'email':kw.get('email')})

    @http.route('/get/otp/timer', type='json', auth='public', website=True, sitemap=False)
    def get_expire_otp_timer(self):
        return ({'timer': request.env.user.company_id.resend_opt_time})

class MatagerWebsiteSale(WebsiteSale):

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        if 'phone_verify_checkbox' not in kw:
            if 'partner_id' in kw and kw.get('partner_id') != '-1':
                partner_id = request.env['res.partner'].sudo().browse(int(kw.get('partner_id')))
                if partner_id.is_phone_verify and 'phone' in kw and  kw.get('phone') == partner_id.phone:
                    kw.update({'phone_verify_checkbox': 'on'})
                elif partner_id.is_phone_verify and 'phone' in kw and  kw.get('phone') != partner_id.phone:
                    if 'phone_verify_checkbox' in kw:
                        kw.pop('phone_verify_checkbox')
                elif partner_id.is_phone_verify:
                    kw.update({'phone_verify_checkbox': 'on'})
        if 'email_verify_checkbox' not in kw:
            if 'partner_id' in kw and kw.get('partner_id') != '-1':
                partner_id = request.env['res.partner'].sudo().browse(int(kw.get('partner_id')))
                if partner_id.is_email_verify and 'email' in kw  and kw.get('email') == partner_id.email:
                    kw.update({'email_verify_checkbox': 'on'})
                elif partner_id.is_email_verify and 'email' in kw and kw.get('email') != partner_id.email:
                    if 'email_verify_checkbox' in kw:
                        kw.pop('email_verify_checkbox')
                elif partner_id.is_email_verify:
                    kw.update({'email_verify_checkbox': 'on'})

        res = super().address(**kw)
        checkout = res.qcontext.get('checkout')
        partner_id = False
        if 'partner_id' in kw and kw.get('partner_id') != '-1':
            partner_id = request.env['res.partner'].sudo().browse(int(kw.get('partner_id')))
        if not bool(checkout) :
            res.qcontext.update({'show_phone_verify':True})
        elif  kw.get('partner_id') != '-1' and partner_id and partner_id.is_phone_verify == False:
            res.qcontext.update({'show_phone_verify': True})
        elif 'phone_verify_checkbox' not in kw or ('phone_verify_checkbox' in kw and kw.get('phone_verify_checkbox') != 'on'):
            res.qcontext.update({'show_phone_verify': True})
        else:
            res.qcontext.update({'show_phone_verify': False})

        if not bool(checkout) :
            res.qcontext.update({'show_email_verify':True})
        elif kw.get('partner_id') != '-1' and partner_id and partner_id.is_email_verify == False:
            res.qcontext.update({'show_email_verify': True})
        elif 'email_verify_checkbox' not in kw  or ('email_verify_checkbox' in kw and kw.get('email_verify_checkbox') != 'on'):
            res.qcontext.update({'show_email_verify': True})
        else:
            res.qcontext.update({'show_email_verify': False})
        return res

    # super call method for removing zip code from mandatory for billing address
    def _get_mandatory_fields_billing(self, country_id=False):
        req = super(MatagerWebsiteSale, self)._get_mandatory_fields_billing(country_id)
        if 'zip' in req:
            req.remove('zip')
        return req

    # super call method for removing zip code from mandatory for shipping address
    def _get_mandatory_fields_shipping(self, country_id=False):
        req = super(MatagerWebsiteSale, self)._get_mandatory_fields_shipping(country_id)
        if 'zip' in req:
            req.remove('zip')
        return req

    # super call method for adding data of building in backend
    def values_postprocess(self, order, mode, values, errors, error_msg):
        new_values, errors, error_msg = super(MatagerWebsiteSale, self).values_postprocess(order, mode, values, errors,
                                                                                           error_msg)
        if 'building' in values:
            if values.get('building') != '':
                new_values.update({'building': values.get('building')})
            else:
                new_values.update({'building': ''})
        if 'phone_verify_checkbox' in values:
            if values.get('phone_verify_checkbox') == 'on':
                new_values.update({'is_phone_verify': True})
        if 'email_verify_checkbox' in values:
            if values.get('email_verify_checkbox') == 'on':
                new_values.update({'is_email_verify': True})
        return new_values, errors, error_msg

    def checkout_form_validate(self, mode, all_form_values, data):
        # super call method for adding phone validation error
        error, error_msg = super(MatagerWebsiteSale, self).checkout_form_validate(mode, all_form_values, data)
        # Phone validation
        if data.get('phone') and len(data.get('phone')) > 8 or len(data.get('phone')) < 8:
            error["phone"] = 'error'
            error_msg.append(_('Invalid phone! Please enter a valid Phone Number.'))
        if 'phone_verify_checkbox' not in all_form_values and 'email_verify_checkbox' not in all_form_values :
            error["phone_verify_checkbox"] = 'missing'
            error["email_verify_checkbox"] = 'missing'
            error_msg.append(_('Please Validate your phone number and email before proceeding further!'))
        elif 'phone_verify_checkbox' not in all_form_values:
            error["phone_verify_checkbox"] = 'missing'
            error_msg.append(_('Please Validate your phone number before proceeding further!'))
        elif 'email_verify_checkbox' not in all_form_values:
            error["email_verify_checkbox"] = 'missing'
            error_msg.append(_('Please Validate your email before proceeding further!'))
        return error, error_msg

    # get google api value from system parameter
    @http.route('/get/googleapikey', type='json', auth="public")
    def get_google_apikey(self, model, domain=None):
        return request.env[model].sudo().search(domain).value

    @http.route(['/map/data/response'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def map_data_response(self, **kw):
        # method call for js to get country and state id
        js_data = {}
        state_data = {}
        country_data = {}
        country = kw.get('country')
        state = kw.get('state')
        state_long_name = kw.get('state_long_name')
        if country:
            country_obj = request.env['res.country'].sudo().search([('code', '=', country)], limit=1)
            js_data.update({'country_id': country_obj.id})
            country_data.update({'display_name': country_obj.name, 'id': country_obj.id})
            if country_obj:
                state_obj = request.env['res.country.state'].sudo().search(
                    [('country_id', '=', country_obj.id), '|', ('code', '=', state), ('name', '=', state_long_name)],
                    limit=1)
                if state_obj:
                    js_data.update({'state_id': state_obj.id})
                    state_data.update({'display_name': state_obj.name, 'id': state_obj.id})
        if js_data:
            if not js_data.get('state_id'):
                js_data.update({'state_id': False})
            if not js_data.get('country_id'):
                js_data.update({'country_id': False})
            if state_data:
                js_data.update({'state_id': state_data})
            else:
                js_data.update({'state_id': False})
            if country_data:
                js_data.update({'country_id': country_data})
            else:
                js_data.update({'country_data': False})
            return js_data
        return False

    # route for all state based on country come from selection in address
    @http.route('/country/get_state', auth='public', type='json', website=True, methods=['POST'])
    def get_zone(self, **kw):
        read_results = request.env['res.country.state'].sudo().search_read([('country_id', '=', kw['country_id'])],
                                                                           ['id', 'name'])
        return read_results
