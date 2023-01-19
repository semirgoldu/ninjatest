# See LICENSE file for full copyright and licensing details
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser
from odoo import api, fields, models


class document_expiry(models.AbstractModel):
    _name = 'report.property_management.report_document_expiry'
    _description = 'Document Expiry Report'

    def get_details(self, start_date, end_date):
        data_1 = []
        certificate_obj = self.env["property.attachment"]
        certificate_ids = certificate_obj.search(
            [('expiry_date', '>=', start_date),
             ('expiry_date', '<=', end_date)])
        for data in certificate_ids:
            data_1.append({
                'name': data.name,
                'property_id': data.property_id.name,
                'expiry_date': data.expiry_date,
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

        detail_res = self.with_context(
            data['form'].get('used_context', {})).get_details(
                start_date, end_date)
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
