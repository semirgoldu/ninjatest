# -*- coding: utf-8 -*-
{
    'name': "ZK Attendance",

    'summary': """
        This module contains for attendance 
        """,

    'description': """
       This module contains for attendance
    """,

    'author': "Intalio",
    'website': "",
    'category': 'HR',
    'version': '15.0.0.0.0.3',
    'depends': ['base', 'web', 'hr_attendance', 'ebs_fusion_hr_employee', 'taqat_groups_access_rights_extended'],
    'data': [
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "views/zk_attendance_form_view.xml",
        "views/res_config_settings_view.xml",
        "views/hr_employee_view.xml",
        "views/attendance_api_log_view.xml",
        "views/hr_attendance.xml",
    ],
}
