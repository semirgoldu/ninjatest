# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Akhilesh N S(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, api, fields


class ValidateLotNumber(models.Model):
    _name = 'serial_no.validation'

    @api.model
    def validate_lots(self, lots, product_id):
        processed = []
        lot_list = []
        price_list = []
        LotObj = self.env['stock.production.lot']
        for lot in lots:
            domain = [('name', '=', lot)]
            if product_id:
                domain.append(('product_id', '=', product_id))
            lot_id = LotObj.search(domain, limit=1)
            try:
                if lot_id.product_qty > 0 and lot not in processed:
                    processed.append(lot)
                    lot_list.append(lot_id.name)
                    price_list.append(lot_id.price_unit)
                    continue
                else:
                    if lot in processed:
                        return ['duplicate', lot]
                    else:
                        return ['no_stock', lot]
            except Exception:
                return ['except', lot]
        return True, sum(price_list)

    @api.model
    def get_lot_price(self, lots):
        LotObj = self.env['stock.production.lot']
        price_list = []
        for lot in lots:
            if lot.get('text') and lot.get('text') != '':
                lot_id = LotObj.search([('name', '=', lot.get('text'))], limit=1)
                price_list.append(lot_id.price_unit)
        return sum(price_list)


class PosOrderLineLotInherit(models.Model):
    _inherit = "pos.pack.operation.lot"

    price_unit = fields.Float()
