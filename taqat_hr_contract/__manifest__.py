# -*- coding: utf-8 -*-
{
    'name': "Taqat Contract Extended Module",

    'summary': """
        This module contains custom modifications for Contract
        """,

    'description': """
       This module contains custom modifications for Contract
    """,

    'author': "TechUltra Solution",
    'website': "http://www.techultrasolution.com/",
    'category': 'HR',
    'version': '15.0.0.0.0.1',
    'depends': [
        'base', 'hr_contract', 'hr_recruitment_custom', 'hr_contract_custom',
    ],
    'data': [
        'reports/employeement_offer.xml',
        'reports/employeement_offer_report.xml',
        'views/hr_contract_view.xml',
    ],


}
