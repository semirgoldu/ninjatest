# -*- coding: utf-8 -*-
{
    'name': "Taqat Purchase Module",

    'summary': """
        This module contains custom modifications for Purchase
        """,

    'description': """
       This module contains custom modifications for Purchase
    """,

    'author': "TechUltra Solution",
    'website': "http://www.techultrasolution.com/",
    'category': 'Purchase',
    'version': '15.0.0.0.0.1',
    'depends': ['purchase','purchase_stock', 'taqat_groups_access_rights_extended', 'taqat_approval_extended'],
    'data': [
        'security/security.xml',
        'views/purchase_order_view.xml',
        'report/purchase_order_report_inherit.xml',
    ],
}
