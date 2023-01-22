# -*- coding: utf-8 -*-
{
    "name": "Odoo Multi Vendor Marketplace Extended",
    "summary": """""",
    "category": "Website",
    "version": "1.1.0",
    "sequence": 1,
    "author": "",
    "license": "",
    "website": "",
    "description": """""",
    "depends": [
        'base','odoo_marketplace', 'base_user_role','marketplace_seller_auction','matager_account_modifier'
    ],
    "data": [
        'security/groups.xml',
    ],
    "application": True,
    "installable": True,
    "auto_install": False,

}
