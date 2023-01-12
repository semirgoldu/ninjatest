# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Original Copyright 2015 Eezee-It, modified and maintained by Odoo.

{
    'name': 'Skip Cash',
    'version': '0.1',
    'category': 'Accounting/Payment Acquirers',
    'sequence': 389,
    'description': """
SkipCash Payment Acquirer for online payments

Implements SkipCashs payment gateway api for payment acquirers .""",
    'author':'Rimes Gold',
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_skipcash_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_skipcash/static/src/js/main.js',
        ],
    },
    'application': True,
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
