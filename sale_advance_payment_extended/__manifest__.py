# -*- coding: utf-8 -*-
{
    'name': "Taqat Advance sale payment extended Module",

    'summary': """
        This module contains custom modifications for Advance sale payment
        """,

    'description': """
       This module contains custom modifications for Advance sale payment extended
    """,

    'author': "TechUltra Solution",
    'website': "http://www.techultrasolution.com/",
    'category': '',
    'version': '15.0.0.0.0.1',
    'depends': ['sale_advance_payment'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/sale_order.xml',
        'wizard/sale_advance_payment_wzd_view.xml',
    ],
}

