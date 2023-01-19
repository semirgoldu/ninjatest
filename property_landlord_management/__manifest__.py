# See LICENSE file for full copyright and licensing details
{
    'name': 'Property Landlord Management',
    'version': '13.0.1.0.0',
    'category': 'Real Estate',
    'summary': """
Property Landlord Management
property owner management
     """,
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'license': 'LGPL-3',
    'website': 'http://www.serpentcs.com',
    'depends': ['property_management'],
    'data': [
        'data/data_landlord_sequence.xml',
        'security/ir.model.access.csv',
        'views/view_analytic_account.xml',
        'views/view_res_partner.xml',
        'views/view_assets_management.xml'
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': True,
    'price' : 49,
    'currency': 'EUR',
}
