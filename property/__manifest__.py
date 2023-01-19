# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details
{
    'name': 'Property Management - Odoo Community Compatible',
    'version': '13.0.1.0.0',
    'category': 'Real Estate',
    'license': 'LGPL-3',
    'sequence': 1,
    'summary': """
        property management
        asset management
        tenancy tenant contract
        recurring contract
        penalty maintenance management
        property sale purchase
        booking management
        property rent sale purchase
     """,
     'description': """
        property management
        asset management
        tenancy tenant contract
        recurring contract
        penalty maintenance management
        property sale purchase
        booking management
        property rent sale purchase
     """,
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'https://www.serpentcs.in/product/property-management-system',
    'depends': [
        'property_management',
        'property_recurring_maintenance',
        'property_penalty',
        'property_sale_purchase',
        'property_rent_report',
        'property_booking',
        'property_landlord_management',
        'property_maintenance',
        'multiple_property_rent',
        'property_commission',
        'property_website'],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': True,
    'price' : 9,
    'currency': 'EUR',
}
