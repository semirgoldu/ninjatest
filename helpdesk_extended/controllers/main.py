from odoo import http
from odoo.http import request
from odoo.addons.website_helpdesk.controllers.main import WebsiteHelpdesk
from odoo.tools import is_html_empty



class WebsiteHelpdeskInherit(WebsiteHelpdesk):



    def get_helpdesk_team_data(self, team, search=None):
        return {'team': team}

    @http.route(['/helpdesk', '/helpdesk/<model("helpdesk.team"):team>'], type='http', auth="public", website=True, sitemap=True)
    def website_helpdesk_teams(self, team=None, **kwargs):
        search = kwargs.get('search')
        # For breadcrumb index: get all team
        propertys = []
        if request.env.user:
            property_datas = request.env['account.analytic.account'].sudo().search([('tenant_id','=',request.env.user.tenant_id.id)])
            for property_data in property_datas:
                propertys.append(property_data.property_id)
        teams = request.env['helpdesk.team'].search(['|', '|', ('use_website_helpdesk_form', '=', True), ('use_website_helpdesk_forum', '=', True), ('use_website_helpdesk_slides', '=', True)], order="id asc")
        if not request.env.user.has_group('helpdesk.group_helpdesk_manager'):
            teams = teams.filtered(lambda team: team.website_published)
        if not teams:
            return request.render("website_helpdesk.not_published_any_team")
        result = self.get_helpdesk_team_data(team or teams[0], search=search)
        # For breadcrumb index: get all team
        result['teams'] = teams
        result['is_html_empty'] = is_html_empty
        result['propertys'] = propertys
        return request.render("website_helpdesk.team", result)

    @http.route(['/my/maintenance/<int:ticket_id>/'], type='http', auth="public", website=True)
    def maintenance(self, ticket_id, uuid='', message='', message_class='', **kw):
        maintenance_data = request.env['maintenance.request'].sudo().search([('ticket_id', '=', ticket_id)])
        values = {}
        values.update({
            'maintenances': maintenance_data,
            'page_name': 'Maintenance',
            'default_url': '/my/maintenance',
        })
        return request.render("helpdesk_extended.maintenance_tree_view", values)

    @http.route(['/my/maintenance/record/<int:maintenance_id>/'], type='http', auth="public", website=True)
    def maintenance_record(self, maintenance_id, uuid='', message='', message_class='', **kw):
        maintenance_data = request.env['maintenance.request'].sudo().browse(maintenance_id)
        values = {}
        values.update({
            'maintenance_rec': maintenance_data,
            'page_name': 'Maintenance',
            'default_url': '/my/maintenance/record/',
        })
        return request.render("helpdesk_extended.maintenance_view", values)