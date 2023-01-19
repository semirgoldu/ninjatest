# See LICENSE file for full copyright and licensing details
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.tools import ustr


class tenancy_detail_by_tenant(models.AbstractModel):
    _name = 'report.property_management.report_tenancy_by_tenant'
    _description = 'Tenancy By Tenant'

    def get_details(self, start_date, end_date, tenant_id):
        data_1 = []
        tenancy_obj = self.env["account.analytic.account"]
        tenancy_ids = tenancy_obj.search([
            ('tenant_id', '=', tenant_id[0]),
            ('date_start', '>=', start_date),
            ('date_start', '<=', end_date),
            ('is_property', '=', True)])
        for data in tenancy_ids:
            if data.currency_id:
                cur = data.currency_id.symbol
            data_1.append({
                'property_id': data.property_id.name,
                'date_start': data.date_start,
                'date': data.date,
                'rent': cur + ustr(data.rent),
                'deposit': cur + ustr(data.deposit),
                'rent_type_id': data.rent_type_id.name,
                'rent_type_month': data.rent_type_id.renttype,
                'state': data.state
            })
        return data_1

    @api.model
    def _get_report_values(self, docids, data=None):
        # self.model = self.env.context.get('active_model')
        docs = self.env[self.env.context.get('active_model')].browse(
            self.env.context.get('active_ids', []))

        start_date = data['form'].get('start_date', fields.Date.today())
        end_date = data['form'].get(
            'end_date', str(datetime.now() + relativedelta(
                months=+1, day=1, days=-1))[:10])
        tenant_id = data['form'].get('tenant_id')

        detail_res = self.with_context(data['form'].get(
            'used_context', {})).get_details(
            start_date, end_date, tenant_id)
        docargs = {
            'doc_ids': docids,
            'doc_model': self.env.context.get('active_model'),
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_details': detail_res,
        }
        docargs['data'].update({
            'end_date': docargs.get('data').get('end_date'),
            'start_date': docargs.get('data').get('start_date')})
        return docargs
