# -*- coding: utf-8 -*-
{
    'name': "Taqat POS Module",

    'summary': """
        This module contains custom modifications for pos
        """,

    'description': """
       This module contains custom modifications for pos
    """,

    'author': "TechUltra Solution",
    'website': "http://www.techultrasolution.com/",
    'category': 'Sale',
    'version': '15.0.0.0.0.1',
    'depends': ['base', 'point_of_sale', 'taqat_groups_access_rights_extended'],
    'data': [
        'security/groups.xml',
        'views/stock_view.xml',
        'views/pos_config_view.xml',
        'views/pos_order_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'taqat_pos_extended/static/src/js/models.js',
            'taqat_pos_extended/static/src/js/get_customer.js',
            'taqat_pos_extended/static/src/js/ProductsWidgetControlPanel.js',
            'taqat_pos_extended/static/src/js/PaymentScreen.js',
        ],
        'web.assets_qweb': [
            "taqat_pos_extended/static/src/xml/OrderReceipt.xml",
            "taqat_pos_extended/static/src/xml/payment_screen.xml",
        ],
    },
}
