from odoo import models, fields, api, _


class IrRuleInherit(models.Model):
    _inherit = 'ir.rule'

    def _get_rules(self, model_name, mode='read'):
        # role_list = [self.env.ref('taqat_groups_access_rights_extended.taqat_group_property_manager').id, self.env.ref('taqat_groups_access_rights_extended.taqat_group_property_employee').id, self.env.ref('taqat_groups_access_rights_extended.taqat_group_inventory_manager').id, self.env.ref('taqat_groups_access_rights_extended.taqat_group_hr_manager').id, self.env.ref('taqat_groups_access_rights_extended.taqat_group_sales_manager').id, self.env.ref('taqat_groups_access_rights_extended.taqat_group_accounting_manager').id, self.env.ref('taqat_groups_access_rights_extended.taqat_group_general_manager_assistance').id, self.env.ref('taqat_groups_access_rights_extended.group_procurement_manager_role').id]
        # if (any(item in self.env.user.role_ids.mapped('id') for item in role_list)) and (self.env.user.has_group('sales_team.group_sale_manager') or self.env.user.has_group('hr_attendance.group_hr_attendance_user') or self.env.user.has_group('hr_holidays.group_hr_holidays_user') or self.env.user.has_group('approvals.group_approval_user')) and (model_name == 'crm.lead' or model_name == 'sale.order' or model_name == 'sale.order.line' or model_name == 'hr.attendance' or model_name == 'hr.leave' or model_name == 'approval.request'):
        if (self.env.user.has_group('taqat_groups_access_rights_extended.taqat_group_property_manager_role') or self.env.user.has_group('taqat_groups_access_rights_extended.taqat_group_property_employee_role') or self.env.user.has_group('taqat_groups_access_rights_extended.taqat_group_inventory_manager_role') or self.env.user.has_group('taqat_groups_access_rights_extended.group_employability_manager_role') or self.env.user.has_group('taqat_groups_access_rights_extended.group_operational_employee_role') or self.env.user.has_group('taqat_groups_access_rights_extended.group_operational_manager') or self.env.user.has_group('taqat_groups_access_rights_extended.taqat_group_hr_manager_role') or self.env.user.has_group('taqat_groups_access_rights_extended.taqat_group_sales_manager_role') or self.env.user.has_group('taqat_groups_access_rights_extended.taqat_group_general_manager_assistance_role') or self.env.user.has_group('taqat_approval_extended.group_procurement_manager')) and (self.env.user.has_group('sales_team.group_sale_manager') or self.env.user.has_group('hr_attendance.group_hr_attendance_user') or self.env.user.has_group('hr_holidays.group_hr_holidays_user') or self.env.user.has_group('approvals.group_approval_user')) and (model_name == 'crm.lead' or model_name == 'sale.order' or model_name == 'sale.order.line' or model_name == 'hr.attendance' or model_name == 'hr.leave' or model_name == 'approval.request'):
            if model_name != 'approval.request' and self.env.user.has_group('taqat_groups_access_rights_extended.taqat_group_hr_manager_role'):
                return super(IrRuleInherit, self)._get_rules(model_name, mode='read')
            if model_name == 'approval.request' and (self.env.user.has_group('taqat_approval_extended.group_procurement_manager') or self.env.user.has_group('taqat_groups_access_rights_extended.taqat_group_general_manager_assistance_role')):
                return super(IrRuleInherit, self)._get_rules(model_name, mode='read')
            if mode not in self._MODES:
                raise ValueError('Invalid mode: %r' % (mode,))

            if self.env.su:
                return self.browse(())

            query = """ SELECT r.id FROM ir_rule r JOIN ir_model m ON (r.model_id=m.id)
                        WHERE m.model=%s AND r.active AND r.perm_{mode} AND r.id NOT IN %s
                        AND (r.id IN (SELECT rule_group_id FROM rule_group_rel rg
                                      JOIN res_groups_users_rel gu ON (rg.group_id=gu.gid)
                                      WHERE gu.uid=%s)
                             OR r.global)
                        ORDER BY r.id
                    """.format(mode=mode)
            record_rules = []
            if model_name == 'crm.lead':
                record_rules = [self.env.ref('crm.crm_rule_all_lead').id, self.env.ref('ebs_fusion_crm.crm_rule_own_lead_write').id, self.env.ref('ebs_fusion_crm.crm_rule_admin_user').id]
            elif model_name == 'sale.order':
                record_rules = [self.env.ref('sale.sale_order_see_all').id]
            elif model_name == 'sale.order.line':
                record_rules = [self.env.ref('sale.sale_order_line_see_all').id]
            elif model_name == 'hr.attendance':
                record_rules = [self.env.ref('hr_attendance.hr_attendance_rule_attendance_overtime_manager').id, self.env.ref('hr_attendance.hr_attendance_rule_attendance_manager').id]
            elif model_name == 'hr.leave':
                record_rules = [self.env.ref('hr_holidays.hr_leave_rule_user_read').id]
            elif model_name == 'approval.request':
                record_rules = [self.env.ref('approvals.approval_request_user').id]
            self._cr.execute(query, (model_name, tuple(record_rules), self._uid))
            return self.browse(row[0] for row in self._cr.fetchall())
        else:
            return super(IrRuleInherit, self)._get_rules(model_name, mode='read')