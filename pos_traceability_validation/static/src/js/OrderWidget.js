odoo.define('ebs_pos_extended.OrderWidgetextend', function (require) {
"use strict";

    const { _t } = require('web.core');
    const OrderWidget = require('point_of_sale.OrderWidget');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');
    const { useListener } = require('web.custom_hooks');
    const rpc = require('web.rpc');
     const NumberBuffer = require('point_of_sale.NumberBuffer');
     const { isConnectionError } = require('point_of_sale.utils');

    const OrderWidgetExt = OrderWidget =>
        class extends OrderWidget {
        async _editPackLotLines(event) {
            const orderline = event.detail.orderline;
            const isAllowOnlyOneLot = orderline.product.isAllowOnlyOneLot();
            const packLotLinesToEdit = orderline.getPackLotLinesToEdit(isAllowOnlyOneLot);
            const { confirmed, payload } = await this.showPopup('EditListPopup', {
                title: this.env._t('Lot/Serial Number(s) Required'),
                isSingleItem: isAllowOnlyOneLot,
                array: packLotLinesToEdit,
                product:orderline.get_product().id,
            });
            if (confirmed) {
                // Segregate the old and new packlot lines
                const modifiedPackLotLines = Object.fromEntries(
                    payload.newArray.filter(item => item.id).map(item => [item.id, item.text])
                );
                const newPackLotLines = payload.newArray
                    .filter(item => !item.id)
                    .map(item => ({ lot_name: item.text }));

                orderline.setPackLotLines({ modifiedPackLotLines, newPackLotLines });
            }
            this.order.select_orderline(event.detail.orderline);

             var orderline1 = event.detail.orderline;
             var tracking = orderline1.product.tracking;
            if (tracking == 'serial'){
                var packlotlines = orderline1.getPackLotLinesToEdit();
                const result =  await rpc.query({
                                            model: 'serial_no.validation',
                                            method: 'get_lot_price',
                                            args: [packlotlines]
                                            })
                orderline1.price_manually_set = true;
                orderline1.set_unit_price(result/orderline1.get_quantity());
            }
        }
    }

    Registries.Component.extend(OrderWidget, OrderWidgetExt);

    return OrderWidget;
});