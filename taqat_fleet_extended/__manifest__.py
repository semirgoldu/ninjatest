# -*- coding: utf-8 -*-
{
    'name': "Taqat Fleet Module",

    'summary': """
        This module contains custom modifications for Fleet
        """,

    'description': """
       This module contains custom modifications for Fleet 
    """,

    'author': "TechUltra Solution",
    'website': "http://www.techultrasolution.com/",
    'category': 'Product',
    'version': '15.0.0.0.0.1',
    'depends': ['fleet', 'taqat_donation'],
    'data': [
        'security/groups.xml',
        'views/fleet_extended_view.xml',
        'views/fleet_vehicle_views_inherit.xml',
    ],
}
