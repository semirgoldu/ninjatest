# -*- coding: utf-8 -*-
{
    'name': "Donation Order",

    'summary': """
        This module contains for Donation Order
        """,

    'description': """
       This module contains for Donation Order
    """,

    'author': "Intalio",
    'website': "",
    'category': 'Product',
    'version': '15.0.0.0.0.3',
    'depends': ['mail', 'product', 'stock','taqat_webcam', 'taqat_groups_access_rights_extended'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/product_template.xml',
        'views/product_template_view.xml',
        'views/donation_type_view.xml',
        'views/containers_schedule_view.xml',
        'views/donation_order_view.xml',
        'views/donation_containers_view.xml',
        'views/stock_picking_view.xml',
        'views/stock_production_lot_view.xml',
        'views/container_order_view.xml',
        'views/res_users.xml',
        'reports/reports.xml',
        'reports/donation_report.xml',
        'reports/container_code_report.xml',
        'wizards/add_donation_product_wizard_view.xml',
    ],
}
