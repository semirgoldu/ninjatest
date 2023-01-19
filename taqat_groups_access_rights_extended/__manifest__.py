# -*- coding: utf-8 -*-
{
    'name': "Taqat Access Right Module",

    'summary': """
        This module contains custom modifications for Configuration
        """,

    'description': """
       This module contains custom modifications for Configuration
    """,

    'author': "TechUltra Solution",
    'website': "http://www.techultrasolution.com/",
    'category': 'Configuration',
    'version': '15.0.0.0.0.1',
    'depends': ['base_user_role','ebs_fusion_hr_employee','hr_contract_custom','hr_holidays','hr_appraisal','sales_team','hr_recruitment','hr_payroll','account','hr_attendance','base', 'approvals','im_livechat', 'ebs_qsheild_mod', 'taqat_approval_extended', 'stock','hide_menu_user', 'maintenance', 'social', 'survey', 'hr_work_entry', 'analytic'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/hr_holiday_views.xml',
        'views/user_role_views.xml',
    ],
}
