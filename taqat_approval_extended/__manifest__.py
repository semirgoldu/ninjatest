# -*- coding: utf-8 -*-
{
    'name': "Taqat Approval",

    'summary': """
        This module contains custom modifications for Approval
        """,

    'description': """
       This module contains custom modifications for Approval
    """,

    'author': "Intalio",
    'website': "",
    'category': 'Product',
    'version': '15.0.0.0.0.1',
    'depends': ['approvals_purchase','hr_approvals', 'purchase_requisition'],
    'data': [
        'security/groups.xml',
        'views/approvals_request_view.xml',
        'views/purchase_requisition_form.xml',
        'views/account_invoice_form.xml',
    ],
}
