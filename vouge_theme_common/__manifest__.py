# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    # Theme information
    'name': 'Bizople Theme Common',
    'category': 'Website',
    'version': '15.0.1.2',
    'author': 'Bizople Solutions Pvt. Ltd.',
    'website': 'https://www.bizople.com',
    'summary': 'Bizople Theme Common',
    'description': """Bizople Theme Common""",
    'depends': [
        'website',
        'website_blog',
        'portal',
        'theme_default',
        'web_editor',
        'website_sale',
        'website_sale_wishlist',
        'website_sale_comparison',
        'website_sale_stock',
    ],

    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/manifest.xml',
        'views/pwa_offline.xml',
        'views/brand_template.xml',
        'views/category_template.xml',
        #Megamenus
        'views/megamenus/megamenu_one_snippet.xml',
        'views/megamenus/megamenu_two_snippet.xml',
        'views/megamenus/megamenu_three_snippet.xml',
        'views/megamenus/megamenu_four_snippet.xml',
        'views/megamenus/megamenu_five_snippet.xml',
        'views/megamenus/megamenu_six_snippet.xml',
    ],

    'images': [
        'static/description/banner.jpg'
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
    'price': 25,
    'currency': 'EUR',
}
