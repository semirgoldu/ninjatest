# See LICENSE file for full copyright and licensing details
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db
import werkzeug
import logging
import werkzeug.utils
import odoo.addons.website_sale.controllers.main
from odoo import http, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.http import request, serialize_exception as _serialize_exception

db_list = http.db_list
db_monodb = http.db_monodb

_logger = logging.getLogger(__name__)


def db_info():
    version_info = odoo.service.common.exp_version()
    return {
        'server_version': version_info.get('server_version'),
        'server_version_info': version_info.get('server_version_info'),
    }


class PropertyManagementLogin(odoo.addons.web.controllers.main.Home):

    

    @http.route()
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                return super(PropertyManagementLogin, self).web_login(*args, **kw)
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error1"] = _(
                        "Another user is already registered using this email address.")
                else:
                    _logger.error(e.message)
                    qcontext['error1'] = _("Could not create a new account.")
        if qcontext['login']:
            qcontext['login1'] = qcontext.pop('login')
        return http.local_redirect('/web/login', qcontext)
