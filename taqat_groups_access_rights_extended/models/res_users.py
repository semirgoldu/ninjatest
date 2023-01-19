from odoo import models, fields, api, _


class ResUsersRoleInherit(models.Model):
    _inherit = "res.users.role"

    menu_items_ids = fields.Many2many('ir.ui.menu', string="Menu", store=True,
                                      help='Select menu items that needs to be '
                                           'hidden to this user ')


class ResUsers(models.Model):
    _inherit = 'res.users'

    # child_ids = fields.Many2many('res.users', compute="get_users_child")
    #
    # def get_users_child(self):
    #     for rec in self:
    #         child = self.get_child_ids(self.employee_ids.ids)
    #         rec.child_ids = [(6, 0, self.env['hr.employee'].browse(child).mapped('user_id').ids)]
    #
    # def get_child_ids(self, employees):
    #     child = []
    #     for employee in self.env['hr.employee'].browse(employees):
    #         if employee.child_ids:
    #             bom_lines = employee.child_ids
    #             child += employee.ids
    #             result = self.get_child_ids(bom_lines.ids)
    #             child += result + bom_lines.ids
    #         else:
    #             child.append(employee.id)
    #     return child

    hide_menu_ids = fields.Many2many('ir.ui.menu', string="Menu", store=True,
                                     help='Select menu items that needs to be '
                                          'hidden to this user', compute="onchange_role_user")

    @api.onchange('role_line_ids', 'role_ids', 'role_ids.menu_items_ids')
    @api.depends('role_line_ids', 'role_ids', 'role_ids.menu_items_ids')
    def onchange_role_user(self):
        for rec in self:
            rec.hide_menu_ids = [(6, 0, rec.role_line_ids.mapped('role_id').mapped('menu_items_ids').ids)]