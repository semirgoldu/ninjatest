from odoo import _, api, fields, models
from collections import defaultdict
from odoo.addons.stock.wizard.product_label_layout import ProductLabelLayout
import odoo.addons.product.report.product_label_report
from odoo.exceptions import UserError, ValidationError

def _prepare_data(env, data):
    # change product ids by actual product object to get access to fields in xml template
    # we needed to pass ids because reports only accepts native python types (int, float, strings, ...)
    if data.get('active_model') == 'product.template':
        Product = env['product.template'].with_context(display_default_code=False)
    elif data.get('active_model') == 'product.product':
        Product = env['product.product'].with_context(display_default_code=False)
    else:
        raise UserError(_('Product model not defined, Please contact your administrator.'))

    total = 0
    quantity_by_product = defaultdict(list)
    for p, q in data.get('quantity_by_product').items():
        product = Product.browse(int(p))
        if isinstance(q, list):
            quantity_by_product[product].append((product.barcode, q[0][0], q[0][1]))
            total += q[0][0]
        else:
            quantity_by_product[product].append((product.barcode, q, product.lst_price if product.is_product_variant else product.list_price))
            total += q
    if data.get('custom_barcodes'):
        # we expect custom barcodes format as: {product: [(barcode, qty_of_barcode)]}
        for product, barcodes_qtys in data.get('custom_barcodes').items():
            quantity_by_product[Product.browse(int(product))] += (barcodes_qtys)
            total += sum(qty for _, qty, price in barcodes_qtys)

    layout_wizard = env['product.label.layout'].browse(data.get('layout_wizard'))
    if not layout_wizard:
        return {}

    return {
        'quantity': quantity_by_product,
        'rows': layout_wizard.rows,
        'columns': layout_wizard.columns,
        'page_numbers': (total - 1) // (layout_wizard.rows * layout_wizard.columns) + 1,
        'price_included': data.get('price_included'),
        'extra_html': layout_wizard.extra_html,
    }

odoo.addons.product.report.product_label_report._prepare_data = _prepare_data

class ProductLabelLayoutInherit(models.TransientModel):
    _inherit = 'product.label.layout'

    def _prepare_report_data(self):
        xml_id, data = super(ProductLabelLayout, self)._prepare_report_data()

        if 'zpl' in self.print_format:
            xml_id = 'stock.label_product_product'

        if self.picking_quantity == 'picking':
            qties = defaultdict(list)
            custom_barcodes = defaultdict(list)
            uom_unit = self.env.ref('uom.product_uom_categ_unit', raise_if_not_found=False)
            for line in self.move_line_ids:
                if line.product_uom_id.category_id == uom_unit:
                    if (line.lot_id or line.lot_name) and int(line.qty_done):
                        custom_barcodes[line.product_id.id].append((line.lot_id.name or line.lot_name, int(line.qty_done), line.price_unit or 0))
                        continue
                    qties[line.product_id.id].append((line.qty_done, line.price_unit))
            # Pass only products with some quantity done to the report
            data['quantity_by_product'] = {p: q for p, q in qties.items() if q}
            data['custom_barcodes'] = custom_barcodes
        return xml_id, data
