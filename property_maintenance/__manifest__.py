# See LICENSE file for full copyright and licensing details

{
    'name': 'Property Maintenance',
    'version': '13.0.1.0.0',
    'category': 'Real Estate',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'summary': """
You can manage maintenance of property
maintenance management
building maintenance
maintenance schedule
maintenance calendar
maintenance process
maintenance statistics
    """,
    'license': 'LGPL-3',
    'website': 'http://www.serpentcs.com',
    'depends': ['property_management', 'maintenance'],
    'data': [
        'security/maint_security.xml',
        'security/ir.model.access.csv',
        'views/asset_management_view.xml',
        'views/maintenance_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': True,
    'price' : 49,
    'currency': 'EUR',
}
