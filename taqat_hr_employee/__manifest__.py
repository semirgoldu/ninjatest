# -*- coding: utf-8 -*-
{
    'name': "Hr Employee Extended Module",

    'summary': """
        This module contains custom modifications for Hr Employee
        """,

    'description': """
       This module contains custom modifications for  Hr Employee
    """,

    'author': "TechUltra Solution",
    'website': "http://www.techultrasolution.com/",
    'category': 'HR',
    'version': '15.0.0.0.0.1',
    'depends': [
        'hr',
        'base',
        'hr_employee_custom',
    ],
    'data': [
        'data/sequence.xml',
        'views/hr_employee_view.xml',
    ],


}
