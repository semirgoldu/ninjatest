# See LICENSE file for full copyright and licensing details
from odoo import fields, models, api


class LandlordPartner(models.Model):
    _name = "landlord.partner"
    _description = 'Landlord Partner'
    _inherits = {'res.partner': 'parent_id'}

    doc_name = fields.Char(
        string='Filename')
    id_attachment = fields.Binary(
        string='Identity Proof')
    owner_tenancy_ids = fields.One2many(
        comodel_name='account.analytic.account',
        inverse_name='property_owner_id',
        string='Landlord Details',
        help='Landlord Details')
    parent_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
        index=True,
        ondelete='cascade')

    @api.model
    def create(self, vals):
        """
        This Method is used to override orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        property_user = False
        res = super(LandlordPartner, self).create(vals)
        if self._context.get('is_owner'):
            password = self.env['res.company'].browse(
                vals.get('company_id', False)).default_password
            if not password:
                password = ''
            admin_user = self.env['res.users'].search([('groups_id','=',self.env.ref('base.group_system').id)],limit=1)
            create_user = self.env['res.users'].with_user(admin_user.id).create({
                'login': vals.get('email'),
                'name': vals.get('name'),
                'password': password,
                'partner_id': res.parent_id.id,
                'sel_groups_%s_%s_%s' % (self.env.ref('base.group_user').id, self.env.ref('base.group_portal').id,
                                         self.env.ref('base.group_public').id): self.env.ref('base.group_portal').id,
            })
            # if res.customer_rank > 0:
            #     property_user = \
            #         self.env.ref('property_management.group_property_user')
            # if res.agent:
            #     property_user = \
            #         self.env.ref('property_management.group_property_agent')
            # if res.is_owner:
            #     property_user = \
            #         self.env.ref('property_management.group_property_owner')
            # if property_user:
            #     property_user.write({'users': [(4, create_user.id)]})
        return res

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_owner = fields.Boolean(
        string='Is a Owner',
        help="Check this box if this contact is a landlord(owner).")
    
