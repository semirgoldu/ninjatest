# -*- coding: utf-8 -*-
{
    'name': "Property Management Extended Module",

    'summary': """
        This module contains custom modifications for Property Management
        """,

    'description': """
       This module contains custom modifications for  Property Management
    """,

    'author': "TechUltra Solution",
    'website': "http://www.techultrasolution.com/",
    'category': 'HR',
    'version': '15.0.0.0.0.1',
    'depends': [
        'property_management', 'taqat_groups_access_rights_extended', 'report_xlsx'
    ],
    'data': [
        'data/mail_activity.xml',
        'data/ir_cron.xml',
        'data/contract_mail_template.xml',
        'security/ir.model.access.csv',
        'views/property_management_view.xml',
        'views/mass_duplicate_view.xml',
        'views/tenancy_partner_view.xml',
        'views/tenancy_tenant_contract_view.xml',
        'views/tenancy_rent_schedule.xml',
        'wizards/custom_report_wizards.xml',
        'wizards/mass_duplicate_wizard_view.xml',
        'report/reports_action.xml',
        'report/tenancy_contract.xml',
        'report/tenancy_contract_report_template.xml',
        'report/tenancy_receipt.xml',
        'report/tenancy_receipt_slip.xml',
        'report/lease_notice.xml',
        'report/lease_notice_report.xml',
        'report/free_rent_report.xml',
    ],


}
