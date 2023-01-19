from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class RealEstateStatement(models.TransientModel):
    _name = 'parent.property.report'

    parent_property_ids = fields.Many2many('account.asset.asset', string="Parent Property")

    def action_confirm(self):
        domain = []
        if self.parent_property_ids:
            domain = [('parent_id', 'in', self.parent_property_ids.ids)]
        data_dict = {}
        for d in self.env['account.asset.asset'].sudo().search(domain):
            if data_dict.get(d.parent_id.id):
                data_dict.get(d.parent_id.id).append(d.id)
            else:
                data_dict.update({d.parent_id.id: [d.id]})
        if data_dict:
            data = {
                'properties': data_dict,
            }
            return self.env.ref('taqat_property_management.action_parent_property_report_xlsx_report').report_action(self,
                                                                                                                 data=data)
        else:
            raise UserError(_("Records not found."))


class MaintenanceReport(models.TransientModel):
    _name = 'maintenance.report'

    parent_property_ids = fields.Many2many('account.asset.asset', string="Parent Property")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    def action_confirm(self):
        domain = []
        if self.parent_property_ids:
            domain = [('property_id', 'in', self.parent_property_ids.ids)]
        if self.from_date:
            domain.append(('request_date', '>=', self.from_date))
        if self.to_date:
            domain.append(('request_date', '<=', self.to_date))
        data_dict = {}
        for d in self.env['maintenance.request'].sudo().search(domain):
            if data_dict.get(d.property_id.id):
                data_dict.get(d.property_id.id).append(d.id)
            else:
                data_dict.update({d.property_id.id: [d.id]})
        if data_dict:
            data = {
                'properties': data_dict,
                'from_date': self.from_date,
                'to_date': self.to_date,
            }
            return self.env.ref('taqat_property_management.action_maintenance_report_xlsx_report').report_action(self,
                                                                                                             data=data)
        else:
            raise UserError(_("Records not found."))


class RealEstateTenancies(models.TransientModel):
    _name = 'real.estate.tenancies'

    parent_property_ids = fields.Many2many('account.asset.asset', string="Parent Property")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    def action_confirm(self):
        tenant_tenancy = self.env['account.analytic.account'].sudo().search([('property_id.parent_id', 'in', self.parent_property_ids.ids)])
        data_dict = {}
        for d in tenant_tenancy.sudo().search([('id', 'in', tenant_tenancy.ids), ('date_start', '>=', self.from_date), ('date', '<=', self.to_date)]):
            if d.property_id.parent_id.id:
                if data_dict.get(d.property_id.parent_id.id):
                    data_dict.get(d.property_id.parent_id.id).append(d.id)
                else:
                    data_dict.update({d.property_id.parent_id.id: [d.id]})
        if data_dict:
            data = {
                'properties': data_dict,
                'from_date': self.from_date,
                'to_date': self.to_date,
            }
            return self.env.ref('taqat_property_management.action_real_estate_tenant_tenancies_xlsx_report').report_action(self, data=data)
        else:
            raise UserError(_("Records not found."))


class RealEstateTenanciesLines(models.TransientModel):
    _name = 'real.estate.tenancies.lines'

    parent_property_ids = fields.Many2many('account.asset.asset', string="Parent Property")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    def action_confirm(self):
        tenant_tenancy = self.env['account.analytic.account'].sudo().search([('property_id.parent_id', 'in', self.parent_property_ids.ids)])
        data_dict = {}
        for d in tenant_tenancy.sudo().search([('id', 'in', tenant_tenancy.ids), ('state', 'in', ['open']), ('date_start', '>=', self.from_date), ('date', '<=', self.to_date)]):
            if d.property_id.parent_id.id:
                if data_dict.get(d.property_id.parent_id.id):
                    data_dict.get(d.property_id.parent_id.id).append(d.id)
                else:
                    data_dict.update({d.property_id.parent_id.id: [d.id]})
        if data_dict:
            data = {
                'properties': data_dict,
                'from_date': self.from_date,
                'to_date': self.to_date,
            }
            return self.env.ref('taqat_property_management.action_real_tenant_tenancies_lines_xlsx_report').report_action(self, data=data)
        else:
            raise UserError(_("Records not found."))


class VacanciesReport(models.TransientModel):
    _name = 'vacancies.report'

    parent_property_ids = fields.Many2many('account.asset.asset', string="Parent Property")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    def action_confirm(self):
        properties = self.env['account.asset.asset'].sudo().search([('parent_id', 'in', self.parent_property_ids.ids)])
        data_dict = {}
        for d in properties.sudo().search([('id', 'in', properties.ids)]):
            if d.parent_id.id:
                if data_dict.get(d.parent_id.id):
                    data_dict.get(d.parent_id.id).append(d.id)
                else:
                    data_dict.update({d.parent_id.id: [d.id]})
        if data_dict:
            data = {
                'properties': data_dict,
                'from_date': self.from_date,
                'to_date': self.to_date,
            }
            return self.env.ref(
                'taqat_property_management.action_vacancies_report_xlsx_report').report_action(self, data=data)
        else:
            raise UserError(_("Records not found."))


class RealEstateExpense(models.TransientModel):
    _name = 'real.estate.expense'

    parent_property_ids = fields.Many2many('account.asset.asset', string="Parent Property")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    def action_confirm(self):
        properties = self.env['account.analytic.account'].sudo().search([('property_id.parent_id', 'in', self.parent_property_ids.ids), ('ten_date', '>=', self.from_date),
                         ('ten_date', '<=', self.to_date)])
        data_dict = {}
        for d in properties.sudo().search([('id', 'in', properties.ids)]):
            if d.property_id.parent_id.id:
                if data_dict.get(d.property_id.parent_id.id):
                    data_dict.get(d.property_id.parent_id.id).append(d.id)
                else:
                    data_dict.update({d.property_id.parent_id.id: [d.id]})
        if data_dict:
            data = {
                'properties': data_dict,
                'from_date': self.from_date,
                'to_date': self.to_date,
            }
            return self.env.ref(
                'taqat_property_management.action_real_tenant_expense_xlsx_report').report_action(self, data=data)
        else:
            raise UserError(_("Records not found."))


class RealEstateRevenue(models.TransientModel):
    _name = 'real.estate.revenue'

    parent_property_ids = fields.Many2many('account.asset.asset', string="Parent Property")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    def action_confirm(self):
        properties = self.env['account.analytic.account'].sudo().search(
            [('property_id.parent_id', 'in', self.parent_property_ids.ids), ('ten_date', '>=', self.from_date),
             ('ten_date', '<=', self.to_date)])
        data_dict = {}
        for d in properties.sudo().search([('id', 'in', properties.ids)]):
            if d.property_id.parent_id.id:
                if data_dict.get(d.property_id.parent_id.id):
                    data_dict.get(d.property_id.parent_id.id).append(d.id)
                else:
                    data_dict.update({d.property_id.parent_id.id: [d.id]})
        if data_dict:
            data = {
                'properties': data_dict,
                'from_date': self.from_date,
                'to_date': self.to_date,
            }
            return self.env.ref(
                'taqat_property_management.action_real_tenant_revenue_xlsx_report').report_action(self, data=data)
        else:
            raise UserError(_("Records not found."))