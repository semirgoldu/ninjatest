{
    'name': 'Matager Shop Modifier',
    'version': '15.0.1',
    'summary': 'E-commerce',
    'description': 'E-commerce Modification',
    'category': 'Website',
    'author': '',
    'website': '',
    'depends': ['vouge_theme_common', 'sale', 'gift_card'],
    'data': [
        'data/ir_cron.xml',
        'views/sale_order_extended_view.xml',
        'views/sale_order_portal_extended_view.xml',
        'views/gift_card_extended_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/matager_shop_modifier/static/src/js/saleorder_return.js',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False
}
