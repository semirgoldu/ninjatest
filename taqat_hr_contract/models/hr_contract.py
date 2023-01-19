from odoo import models, fields, api, _


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    grade = fields.Char(string="Grade")
    is_car_provided = fields.Boolean(default=False, string="Is car Provided?")
    airport = fields.Char(string="Airport")

    def suffix(self, day):
        suffix = ""
        day = int(day)
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        return suffix
    

