# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo 13 Assets Management',
    'version': '13.0.1.0.0',
    'author': 'Odoo Mates, Odoo SA',
    'depends': ['account'],
    'description': """Manage assets owned by a company or a person. 
    Keeps track of depreciation's, and creates corresponding journal entries""",
    'summary': 'Odoo 13 Assets Management',
    'category': 'Accounting',
    'sequence': 32,
    'website': 'http://odoomates.tech',
    'license': 'LGPL-3',
    'images': ['static/description/assets.gif'],
    'data': [
        'security/account_asset_security.xml',
        'security/ir.model.access.csv',
        'wizard/asset_depreciation_confirmation_wizard_views.xml',
        'wizard/asset_modify_views.xml',
        'views/account_asset_views.xml',
        'views/account_invoice_views.xml',
        # 'views/account_asset_templates.xml',
        'views/product_views.xml',
        # 'views/res_config_settings_views.xml',
        'report/account_asset_report_views.xml',
        'data/account_asset_data.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'ow_account_asset/static/src/scss/account_asset.scss',
            'ow_account_asset/static/src/js/account_asset.js',
        ],
        'web.qunit_suite_tests': [
            'ow_account_asset/static/tests/account_asset_tests.js',
        ],
        },
}
