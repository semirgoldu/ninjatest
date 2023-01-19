from odoo import fields, api, models, _
import datetime


class RealEstateStatementExcelReport(models.AbstractModel):
    _name = 'report.taqat_property_management.parent_property_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('بيان العقارات')
        data_format = workbook.add_format({'align': 'center'})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
        # date_format = workbook.add_format({'num_format': 'd-m-yyyy', 'align': 'center'})
        sheet.right_to_left()

        properties = self.env['account.asset.asset'].browse(data.get('properties'))

        row = 0
        col = 0
        if properties:
            sheet.write(row, col, 'م', header_row_style)
            sheet.set_column(col + 1, col + 1, 35)
            sheet.write(row, col + 1, 'العقار', header_row_style)
            sheet.write(row, col + 2, 'نوع الملكية', header_row_style)
            sheet.set_column(col + 3, col + 3, 30)
            sheet.write(row, col + 3, 'الموقع', header_row_style)
            sheet.set_column(col + 4, col + 8, 10)
            sheet.write(row, col + 4, 'القيمة الدفترية', header_row_style)
            sheet.write(row, col + 5, 'القيمة السوقية', header_row_style)
            sheet.write(row, col + 6, 'مساحة الأرض', header_row_style)
            sheet.write(row, col + 7, 'قيمة الفوت', header_row_style)
            sheet.write(row, col + 8, 'قيمة المباني', header_row_style)
            row += 1
            counter = 1
            data_dict = data.get('properties')
            for key, value in data_dict.items():
                parent_id = self.env['account.asset.asset'].browse(int(key))
                sheet.write(row, col, counter, data_format)
                sheet.write(row, col + 1, parent_id.name if parent_id else "", data_format)
                row += 1
                counter += 1
                for rec in value:
                    child_id = self.env['account.asset.asset'].browse(rec)
                    address = ''
                    address += str(child_id.street) if child_id.street else ''
                    address += str(child_id.street2) if child_id.street2 else ''
                    address += str(child_id.zone) if child_id.zone else ''
                    address += str(child_id.building) if child_id.building else ''
                    sheet.write(row, col, counter, data_format)
                    sheet.write(row, col + 1, child_id.name if child_id else "", data_format)
                    sheet.write(row, col + 2, child_id.type_id.name if child_id.type_id else "", data_format)
                    sheet.write(row, col + 3, address, data_format)
                    sheet.write(row, col + 4, child_id.value if child_id.value else "", data_format)
                    sheet.write(row, col + 5, child_id.market_value if child_id.market_value else "", data_format)
                    sheet.write(row, col + 6, child_id.gfa_meter if child_id.gfa_meter else "", data_format)
                    sheet.write(row, col + 7, child_id.gfa_feet if child_id.gfa_feet else "", data_format)
                    sheet.write(row, col + 8, sum(child_id.child_ids.mapped('value')) if child_id.child_ids else "", data_format)
                    row += 1
                    counter += 1
                row += 4


class MaintenanceReport(models.AbstractModel):
    _name = 'report.taqat_property_management.maintenance_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('تقرير الصيانة')
        data_format = workbook.add_format({'align': 'center'})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
        sheet.right_to_left()

        # properties = self.env['account.asset.asset'].browse(data.get('properties'))
        from_date = data.get('from_date')
        to_date = data.get('to_date')

        row = 0
        col = 0
        cost = []
        if data.get('properties'):
            sheet.write(row, col, 'م', header_row_style)
            sheet.set_column(col + 1, col + 1, 35)
            sheet.write(row, col + 1, 'اسم العقار', header_row_style)
            sheet.set_column(col + 2, col + 2, 30)
            sheet.write(row, col + 2, 'الوحدة', header_row_style)
            sheet.write(row, col + 3, 'اجمالي الصيانة', header_row_style)
            sheet.set_column(col + 4, col + 5, 10)
            sheet.write(row, col + 4, 'الموازنة  التقديرية', header_row_style)
            sheet.write(row, col + 5, 'الفرق', header_row_style)
            row += 1
            data_dict = data.get('properties')
            counter = 1
            for key, value in data_dict.items():
                parent_id = self.env['account.asset.asset'].browse(int(key))
                sheet.write(row, col, counter, data_format)
                sheet.write(row, col + 1, parent_id.name if parent_id.name else "", data_format)
                row += 1
                counter += 1
                for rec in value:
                    child_id = self.env['maintenance.request'].browse(rec)
                    sheet.write(row, col, counter, data_format)
                    sheet.write(row, col + 2, child_id.property_id.name if child_id.property_id.name else "", data_format)
                    sheet.write(row, col + 3, child_id.cost if child_id else 0.00, data_format)
                    cost.append(child_id.cost if child_id else 0.00)
                    sheet.write(row, col + 4, '', data_format)
                    sheet.write(row, col + 5, '', data_format)
                    row += 1
                    counter += 1
                sheet.write(row, col, "Total by parent property", data_format)
                sheet.write(row, col+1, sum(parent_id.maintenance_ids.mapped('cost')), data_format)
                row += 5
            sheet.write(row, col, "Total", data_format)
            sheet.write(row, col + 1, sum(cost), data_format)


class RealEstateTenanciesExcelReport(models.AbstractModel):
    _name = 'report.taqat_property_management.real_estate_tenancies_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('تقرير العقود')
        data_format = workbook.add_format({'align': 'center'})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
        date_format = workbook.add_format({'num_format': 'd-m-yyyy', 'align': 'center'})
        sheet.right_to_left()
        row = 0
        col = 0
        cost = []
        if data.get('properties'):
            sheet.set_column(0, 5, 18)
            sheet.write(row, col, 'م', header_row_style)
            sheet.write(row, col + 1, 'العقار', header_row_style)
            sheet.write(row, col + 2, 'الوحدة', header_row_style)
            sheet.write(row, col + 3, 'اسم المستأجر', header_row_style)
            sheet.write(row, col + 4, 'بداية العقد', header_row_style)
            sheet.write(row, col + 5, 'نهاية العقد', header_row_style)
            sheet.write(row, col + 6, 'قيمة العقد', header_row_style)
            sheet.write(row, col + 7, 'فترة السماح', header_row_style)
            sheet.write(row, col + 8, 'الجنسية', header_row_style)
            sheet.write(row, col + 9, 'رقم الهاتف', header_row_style)
            sheet.write(row, col + 10, 'البريد الالكتروني', header_row_style)
            sheet.write(row, col + 11, 'ص. ب', header_row_style)
            sheet.write(row, col + 12, 'التأمين / نقدي / شيك', header_row_style)
            row += 1
            data_dict = data.get('properties')
            counter = 1
            for key, value in data_dict.items():
                parent_id = self.env['account.asset.asset'].browse(int(key))
                sheet.write(row, col, counter, data_format)
                sheet.write(row, col + 1, parent_id.name if parent_id else "", data_format)
                row += 1
                counter += 1
                total_rent = []
                for rec in value:
                    child_id = self.env['account.analytic.account'].browse(rec)
                    sheet.write(row, col, counter, data_format)
                    sheet.write(row, col + 2, child_id.property_id.name if child_id.property_id.name else "", data_format)
                    sheet.write(row, col + 3, child_id.tenant_id.name if child_id.tenant_id else "", data_format)
                    sheet.write(row, col + 4, child_id.date_start if child_id.date_start else "", date_format)
                    sheet.write(row, col + 5, child_id.date if child_id.date else "", date_format)
                    sheet.write(row, col + 6, child_id.total_rent if child_id.total_rent else "", data_format)
                    cost.append(child_id.total_rent)
                    total_rent.append(child_id.total_rent)
                    sheet.write(row, col + 7, child_id.free_months if child_id.free_months else "", data_format)
                    sheet.write(row, col + 8, child_id.tenant_id.nationality_id.name if child_id.tenant_id and child_id.tenant_id.nationality_id else "", data_format)
                    sheet.write(row, col + 9, child_id.tenant_id.mobile if child_id.tenant_id and child_id.tenant_id.mobile else "", data_format)
                    sheet.write(row, col + 10, child_id.tenant_id.email if child_id.tenant_id and child_id.tenant_id.email else "", data_format)
                    sheet.write(row, col + 11, child_id.tenant_id.po_box if child_id.tenant_id and child_id.tenant_id.po_box else "", data_format)
                    sheet.write(row, col + 12, child_id.deposit if child_id.deposit else "", data_format)
                    row += 1
                    counter += 1
                sheet.write(row, col, "Total by parent property", data_format)
                sheet.write(row, col + 1, sum(total_rent), data_format)
                row += 5
            sheet.write(row, col, "Total", data_format)
            sheet.write(row, col + 1, sum(cost), data_format)


class RealEstateTenanciesLinesReport(models.AbstractModel):
    _name = 'report.taqat_property_management.tenancies_lines_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('تقرير العقود')
        data_format = workbook.add_format({'align': 'center'})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
        date_format = workbook.add_format({'num_format': 'd-m-yyyy', 'align': 'center'})
        sheet.right_to_left()

        row = 0
        col = 0
        cost = []
        if data.get('properties'):
            sheet.set_column(0, 5, 18)
            sheet.write(row, col, 'م', header_row_style)
            sheet.write(row, col + 1, 'العقار', header_row_style)
            sheet.write(row, col + 2, 'اسم المستأجر', header_row_style)
            sheet.write(row, col + 3, 'بيان الشهور المستحقة', header_row_style)
            sheet.write(row, col + 4, 'اجمالي قيمة المستحق', header_row_style)
            row += 1
            data_dict = data.get('properties')
            counter = 1
            for key, value in data_dict.items():
                parent_id = self.env['account.asset.asset'].browse(int(key))
                sheet.write(row, col, counter, data_format)
                sheet.write(row, col + 1, parent_id.name if parent_id else "", data_format)
                row += 1
                counter += 1
                total_rent = []
                for rec in value:
                    child_id = self.env['account.analytic.account'].browse(rec)
                    sheet.write(row, col, counter, data_format)
                    sheet.write(row, col + 1, child_id.property_id.name if child_id.property_id else "", data_format)
                    sheet.write(row, col + 2, child_id.name if child_id else "", data_format)
                    rent_lines = child_id.rent_schedule_ids.filtered(lambda x:x.paid == False and x.rent_status == 'done') if child_id.rent_schedule_ids else ""
                    sheet.write(row, col + 3, ', '.join(str(rec.month) for rec in rent_lines.mapped('start_date')), date_format)
                    sheet.write(row, col + 4, sum(rent_lines.mapped('amount')) if rent_lines else 0.00, data_format)
                    total_rent.append(sum(rent_lines.mapped('amount')))
                    cost.append(sum(rent_lines.mapped('amount')))
                    row += 1
                    counter += 1
                sheet.write(row, col, "Total by parent property", data_format)
                sheet.write(row, col + 1, sum(total_rent), data_format)
                row += 5
            sheet.write(row, col, "Total", data_format)
            sheet.write(row, col + 1, sum(cost), data_format)


class VacanciesReport(models.AbstractModel):
    _name = 'report.taqat_property_management.vacancies_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('تقرير الوحدات الشاغرة')
        data_format = workbook.add_format({'align': 'center'})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
        date_format = workbook.add_format({'num_format': 'd-m-yyyy', 'align': 'center'})
        sheet.right_to_left()
        row = 0
        col = 0
        if data.get('properties'):
            sheet.write(row, col, 'م', header_row_style)
            sheet.set_column(col + 1, col + 1, 35)
            sheet.write(row, col + 1, 'العقار', header_row_style)
            sheet.set_column(col + 2, col + 2, 15)
            sheet.write(row, col + 2, 'الوحدات الشاغرة', header_row_style)
            sheet.set_column(col + 3, col + 4, 20)
            sheet.write(row, col + 3, 'تاريخ الاخلاء', header_row_style)
            sheet.write(row, col + 4, 'قيمة فترة الاخلاء', header_row_style)
            row += 1
            data_dict = data.get('properties')
            counter = 1
            cost = []
            for key, value in data_dict.items():
                parent_id = self.env['account.asset.asset'].browse(int(key))
                sheet.write(row, col, counter, data_format)
                sheet.write(row, col + 1, parent_id.name if parent_id else "", data_format)
                row += 1
                counter += 1
                total_rent = []
                for rec in value:
                    child_id = self.env['account.asset.asset'].browse(rec)
                    tenancy_id = self.env['account.analytic.account'].sudo().search([('property_id', '=', child_id.id), ('ten_date', '>=', data.get('from_date')), ('ten_date', '<=', data.get('to_date'))], limit=1)
                    if tenancy_id:
                        sheet.write(row, col, counter, data_format)
                        sheet.write(row, col + 1, child_id.name if child_id.name else "", data_format)
                        sheet.write(row, col + 2, "Yes" if child_id.state == 'draft' else "No", data_format)
                        sheet.write(row, col + 3, tenancy_id.ten_date if tenancy_id else "", date_format)
                        sheet.write(row, col + 4, tenancy_id.rent_schedule_ids.filtered(lambda x:x.paid == True)[-1].amount if tenancy_id and tenancy_id.rent_schedule_ids and tenancy_id.rent_schedule_ids.filtered(lambda x:x.paid == True) else 0.00, data_format)
                        total_rent.append((tenancy_id.rent_schedule_ids.filtered(lambda x:x.paid == True)[-1].amount if tenancy_id and tenancy_id.rent_schedule_ids and tenancy_id.rent_schedule_ids.filtered(lambda x:x.paid == True) else 0.00))
                        cost.append((tenancy_id.rent_schedule_ids.filtered(lambda x:x.paid == True)[-1].amount if tenancy_id and tenancy_id.rent_schedule_ids and tenancy_id.rent_schedule_ids.filtered(lambda x:x.paid == True) else 0.00))
                        row += 1
                        counter += 1
                sheet.write(row, col, "Total by parent property", data_format)
                sheet.write(row, col + 1, sum(total_rent), data_format)
                row += 5
            sheet.write(row, col, "Total", data_format)
            sheet.write(row, col + 1, sum(cost), data_format)


class RealEstateExpenseReport(models.AbstractModel):
    _name = 'report.taqat_property_management.expense_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('تقرير المصروفات العقارية')
        data_format = workbook.add_format({'align': 'center'})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
        # date_format = workbook.add_format({'num_format': 'd-m-yyyy', 'align': 'center'})
        sheet.right_to_left()
        row = 0
        col = 0
        if data.get('properties'):
            sheet.write(row, col, 'م', header_row_style)
            sheet.set_column(col + 1, col + 1, 35)
            sheet.write(row, col + 1, 'العقار', header_row_style)
            sheet.write(row, col + 2, 'المصروف الشهري', header_row_style)
            sheet.write(row, col + 3, 'المصروف', header_row_style)
            sheet.write(row, col + 4, 'الموازنة التقديرية', header_row_style)
            sheet.write(row, col + 5, 'الفرق', header_row_style)
            data_dict = data.get('properties')
            row += 1
            counter = 1
            cost = []
            for key, value in data_dict.items():
                property_id = self.env['account.asset.asset'].browse(int(key))
                sheet.write(row, col, counter, data_format)
                sheet.write(row, col + 1, property_id.name if property_id else "", data_format)
                row += 1
                counter += 1
                total_rent = []
                for rec in value:
                    child_id = self.env['account.analytic.account'].browse(rec)
                    sheet.write(row, col, counter, data_format)
                    sheet.write(row, col + 1, child_id.property_id.name if child_id.property_id else "", data_format)
                    if child_id.frequency == 'monthly':
                        monthly_amount = child_id.main_cost if child_id.main_cost else 0.00
                        yearly_amount = child_id.main_cost * 12 if child_id.main_cost else 0.00
                    else:
                        monthly_amount = child_id.main_cost / 12 if child_id.main_cost else 0.00
                        yearly_amount = child_id.main_cost if child_id.main_cost else 0.00
                    sheet.write(row, col + 2, monthly_amount, data_format)
                    sheet.write(row, col + 3, yearly_amount, data_format)
                    total_rent.append(yearly_amount)
                    cost.append(yearly_amount)
                    budget_year = child_id.property_id.budget_expense_ids.filtered(
                        lambda x: x.budget_year == str(datetime.datetime.today().year)).mapped('budget_year')
                    budget_amount = sum(child_id.property_id.budget_expense_ids.filtered(
                        lambda x: x.budget_year == str(datetime.datetime.today().year)).mapped('amount'))
                    sheet.write(row, col + 4, budget_year[0] if budget_year else '', data_format)
                    sheet.write(row, col + 5, budget_amount if budget_amount > 0 else '', data_format)
                    row += 1
                    counter += 1
                sheet.write(row, col, "Total by parent property", data_format)
                sheet.write(row, col + 1, sum(total_rent), data_format)
                row += 5
            sheet.write(row, col, "Total", data_format)
            sheet.write(row, col + 1, sum(cost), data_format)


class RealEstateRevenueReport(models.AbstractModel):
    _name = 'report.taqat_property_management.revenue_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('تقرير الايرادات العقارية')
        data_format = workbook.add_format({'align': 'center'})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
        date_format = workbook.add_format({'num_format': 'd-m-yyyy', 'align': 'center'})
        sheet.right_to_left()
        row = 0
        col = 0
        if data.get('properties'):
            sheet.write(row, col, 'م', header_row_style)
            sheet.set_column(col + 1, col + 1, 35)
            sheet.write(row, col + 1, 'العقار', header_row_style)
            sheet.write(row, col + 2, 'العائد الشهري', header_row_style)
            sheet.write(row, col + 3, 'العائد السنوي', header_row_style)
            sheet.write(row, col + 4, 'العائد الفعلي', header_row_style)
            sheet.write(row, col + 5, 'المستحق', header_row_style)
            sheet.write(row, col + 6, 'الموازنة التقديرية', header_row_style)
            sheet.write(row, col + 7, 'الفرق', header_row_style)
            data_dict = data.get('properties')
            row += 1
            counter = 1
            cost = []
            for key, value in data_dict.items():
                property_id = self.env['account.asset.asset'].browse(int(key))
                sheet.write(row, col, counter, data_format)
                sheet.write(row, col + 1, property_id.name if property_id else "", data_format)
                row += 1
                counter += 1
                total_rent = []
                for rec in value:
                    child_id = self.env['account.analytic.account'].browse(rec)
                    sheet.write(row, col, counter, data_format)
                    sheet.write(row, col + 1, child_id.property_id.name if child_id.property_id else "", data_format)
                    sheet.write(row, col + 2, child_id.rent if child_id.rent else 0.00, data_format)
                    sheet.write(row, col + 3, child_id.total_rent if child_id.total_rent else 0.00, data_format)
                    done_amount = child_id.rent_schedule_ids.filtered(lambda x: x.paid and x.rent_status == 'done').mapped('amount')
                    sheet.write(row, col + 4, sum(done_amount), data_format)
                    not_done_amount = child_id.rent_schedule_ids.filtered(lambda x: x.paid == False and x.rent_status == 'done').mapped('amount')
                    sheet.write(row, col + 5, sum(not_done_amount), data_format)
                    budget_year = child_id.property_id.budget_revenue_ids.filtered(lambda x: x.budget_year == str(datetime.datetime.today().year)).mapped('budget_year')
                    budget_amount = sum(child_id.property_id.budget_revenue_ids.filtered(lambda x: x.budget_year == str(datetime.datetime.today().year)).mapped('amount'))
                    sheet.write(row, col + 6, budget_year[0] if budget_year else '', data_format)
                    sheet.write(row, col + 7, budget_amount if budget_amount > 0 else '', data_format)
                    total_rent.append(child_id.total_rent)
                    cost.append(child_id.total_rent)
                    row += 1
                    counter += 1
                sheet.write(row, col, "Total by parent property", data_format)
                sheet.write(row, col + 1, sum(total_rent), data_format)
                row += 5
            sheet.write(row, col, "Total", data_format)
            sheet.write(row, col + 1, sum(cost), data_format)
