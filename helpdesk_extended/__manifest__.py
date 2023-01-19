# -*- coding: utf-8 -*-
{
    'name': "Helpdesk Extended",

    'summary': """
        This module contains custom modifications for Helpdesk
        """,

    'description': """
       This module contains custom modifications for Helpdesk
    """,

    'author': "Jaafar Khansa",
    'website': "http://www.ever-bs.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'helpdesk','property_management','website_helpdesk','property_maintenance', 'website_helpdesk_form',
    ],

    # always loaded
    'data': [
        "data/website_helpdesk_ext.xml",
        "views/hepdesk_ticket_views.xml",
        "views/helpdesk_template_inherit.xml",
    ]
}