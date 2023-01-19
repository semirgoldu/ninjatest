from odoo import models, fields, api, _


class StockProductionLotInherit(models.Model):
    _inherit = 'stock.production.lot'

    price_unit = fields.Float("Price",)

    def name_get(self):
        res = []
        if 'form_view_ref' and self._context and self._context.get('form_view_ref') == 'stock.view_move_form':
        # if ('params' in self._context and 'model' in self._context.get('params') and self._context.get('params').get('model') == 'stock.picking') or ('active_model' and self._context and self._context.get('active_model') == 'donation.order'):
            for lot in self:
                name = lot.name + ' - ' + str(lot.price_unit) + ' ' + str(lot.company_id.currency_id.symbol)
                res.append((lot.id, name))
        else:
            for lot in self:
                name = lot.name
                res.append((lot.id, name))
        return res
