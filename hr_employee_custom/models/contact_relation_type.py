# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ContactRelationType(models.Model):
    _name = 'contact.relation.type'
    _description = "Contact Relation Type"

    name = fields.Char(
        string="Name",
        required=True)