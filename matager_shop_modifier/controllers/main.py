# -*- coding: utf-8 -*-
import logging

from odoo import http, SUPERUSER_ID, fields
from odoo.http import request
from odoo.addons.vouge_theme_common.controllers.main import PwaMain

_logger = logging.getLogger(__name__)


class MatagerPwaMain(PwaMain):
    @http.route('/sale/return/portal', type='json', auth='public', website=True, sitemap=False)
    def return_sale_portal(self,**kwargs):
        sale_id = request.env['sale.order'].sudo().browse(int(kwargs.get('token').split('?')[0]))
        sale_id.return_requested = True
        return kwargs.get('token')
    
    # override method for search product which are publish on website
    @http.route('/vouge/search/product', type='http', auth='public', website=True, sitemap=False)
    def search_autocomplete(self, term=None, category=None, popupcateg=None):
        if category or popupcateg:
            if category:
                prod_category = request.env["product.public.category"].sudo().search([
                    ('id', '=', category)])

            else:
                prod_category = request.env["product.public.category"].sudo().search([
                    ('id', '=', popupcateg)])
            product_list = []
            for product in prod_category.product_tmpl_ids or prod_category.child_id.product_tmpl_ids:
                product_list.append(product.id)
            # Add filter domain inside search ('is_published', '=', True)
            results = request.env["product.template"].sudo().search(
                [('name', 'ilike', term), ('id', 'in', product_list), ('is_published', '=', True)])
            value = {
                'results': results

            }
            return request.render("theme_vouge.search_vouge", value)
        else:
            # Add filter domain inside search ('is_published', '=', True)
            results = request.env["product.template"].sudo().search(
                [('name', 'ilike', term), ('is_published', '=', True)])
            value = {
                'results': results
            }
            return request.render("theme_vouge.search_vouge", value)
