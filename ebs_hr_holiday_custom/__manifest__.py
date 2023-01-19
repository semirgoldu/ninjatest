# -*- coding: utf-8 -*-
{
    'name': "HR Holiday Custom ",

    'summary': """
        Ebs HR Holiday Custom """,

    'description': """
        Ebs HR Holiday Custom 
    """,

    'author': "ebs",
    'website': "http://www.ever-bs.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_holidays',],

    # always loaded
    'data': [
        'views/leave_changes.xml',
        'views/leave_request_view.xml',
        'views/leave_allocation_request_custom_view.xml',


    ],
    'qweb': [
        'static/src/xml/*.xml',
    ]

}
