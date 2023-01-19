# See LICENSE file for full copyright and licensing details
import time

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools import ustr


class contract_expiry(models.AbstractModel):
    _name = 'report.property_management.report_contract_expiry'
    _description = "Contract Expiry Report"

    def get_details(self, start_date, end_date):
        """
        This method is used to get the data from account analytic account
        between two dates.
        """
        data_1 = []
        tenancy_obj = self.env["account.analytic.account"]
        tenancy_ids = tenancy_obj.search(
            [('date', '>=', start_date),
             ('date', '<=', end_date),
             ('is_property', '=', True)])
        for data in tenancy_ids:
            if data.currency_id:
                cur = data.currency_id.symbol
            data_1.append({
                'name': data.name,
                'property_id': data.property_id.name,
                'tenant_id': data.tenant_id.name,
                'date_start': data.date_start,
                'date': data.date,
                'rent': cur + ustr(data.rent),
                'rent_type_id': data.rent_type_id.name,
                'rent_type_month': data.rent_type_id.renttype,
                'state': data.state
            })
        return data_1

    @api.model
    def _get_report_values(self, docids, data=None):
        # self.model = self.env.context.get('active_model')
        docs = self.env[self.env.context.get('active_model')].browse(self.env.context.get('active_ids', []))

        start_date = data['form'].get('start_date', fields.Date.today())
        end_date = data['form'].get(
            'end_date', str(
                datetime.now() + relativedelta(
                    months=+1, day=1, days=-1))[:10])

        data_res = self.with_context(
            data['form'].get('used_context', {})).get_details(
                start_date, end_date)
        docargs = {
            'doc_ids': docids,
            'doc_model': self.env.context.get('active_model'),
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_details': data_res,
        }
        docargs['data'].update({
            'end_date': docargs.get('data').get('end_date'),
            'start_date': docargs.get('data').get('start_date')})
        return docargs
