# See LICENSE file for full copyright and licensing details
{
    'name': 'Multiple Property Rent',
    'version': '13.0.1.0.0',
    'category': 'Real Estate',
    'license': 'LGPL-3',
    'summary': """
        Manage your Tenancy with multiple property rent
        rent management
        property rent
        multiple property single tenant
     """,
     'description': """
        Manage your Tenancy with multiple property rent
        rent management
        property rent
        multiple property single tenant
     """,
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'https://www.serpentcs.in/product/property-management-system',
    'depends': ['property_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/multiple_property_rent_view.xml'
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': True,
    'price' : 49,
    'currency': 'EUR',
}
