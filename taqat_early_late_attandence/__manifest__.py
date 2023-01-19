# -*- coding: utf-8 -*-
{
    'name': "Taqat Attendance Module",

    'summary': """
        This module contains custom modifications for Attendance Late Checkin Early Checkout
        """,

    'description': """
       This module contains custom modifications for Attendance Late Checkin Early Checkout
    """,

    'author': "TechUltra Solution",
    'website': "http://www.techultrasolution.com/",
    'category': 'Accounting',
    'version': '15.0.0.0.0.1',
    'depends': ['hr_attendance', 'hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/ir_mail_activity.xml',
        'wizard/justification_attendance_wizard_view.xml',
        'views/hr_leave_type_view.xml',
        'views/hr_employee_view.xml',
        'views/justification_late_early_view.xml',
        'views/justification_type_view.xml',
        'views/employee_shortage_hour.xml',
    ],
}
