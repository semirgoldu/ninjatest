odoo.define('pos_traceability_validation.pos_models', function (require) {
"use strict";
    const EditListPopup = require('point_of_sale.EditListPopup');
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    var rpc = require('web.rpc');
    var models = require('point_of_sale.models');

    const PosEditlistpopup = (EditListPopup) =>
        class extends EditListPopup {
             async confirm() {

                 if (this.props.title == 'Lot/Serial Number(s) Required'){

                         var lot_string = this.state.array
                         var lot_names = [];
                         for (var i = 0; i < lot_string.length; i++) {

                            if (lot_string[i].text != ""){
                                lot_names.push(lot_string[i].text);
                            }

                         }

                         const result =  await rpc.query({
                                                model: 'serial_no.validation',
                                                method: 'validate_lots',
                                                args: [lot_names, this.props.product.id]
                                                })

                            if(result[0] != true){
                                if(result[0] == 'no_stock'){
                                    this.props.resolve({ confirmed: false, payload: await this.getPayload() });
                                    this.trigger('close-popup');
                                    return this.showNotification(
                                        _.str.sprintf(this.env._t("Insufficient stock for " + result[1])),
                                        3000
                                    );
//                                    return this.showPopup('ErrorPopup', {
//                                        'title': this.env._t('Insufficient stock'),
//                                        'body': this.env._t("Insufficient stock for " + result[1]),
//                                    });
                                }
                                else if(result[0] == 'duplicate'){
                                    this.props.resolve({ confirmed: false, payload: await this.getPayload() });
                                    this.trigger('close-popup');
                                    return this.showNotification(
                                        _.str.sprintf(this.env._t("Duplicate entry for " + result[1])),
                                        3000
                                    );
//                                    return this.showPopup('ErrorPopup', {
//                                        'title': this.env._t('Duplicate entry'),
//                                        'body': this.env._t("Duplicate entry for " + result[1]),
//                                    });
                                }
                                else if(result[0] == 'except'){
                                    this.props.resolve({ confirmed: false, payload: await this.getPayload() });
                                    this.trigger('close-popup');
                                    return this.showNotification(
                                        _.str.sprintf(this.env._t("Exception occured with" + result[1])),
                                        3000
                                    );
//                                    alert("Exception occured with " + result[1])
//                                    return this.showPopup('ErrorPopup', {
//                                        'title': this.env._t('Exception'),
//                                        'body': this.env._t("Exception occured with" + result[1]),
//                                    });
                                }
                            }
                            else{
                                this.props.resolve({ confirmed: true, payload: await this.getPayload() });
                                this.trigger('close-popup');
//                                if(result.length > 0){
//                                    var line = this.env.pos.get_order().get_selected_orderline();
//                                    if (line !== undefined){
//                                        var packlotlines = line.getPackLotLinesToEdit();
//                                        const price =  await rpc.query({
//                                                model: 'serial_no.validation',
//                                                method: 'get_lot_price',
//                                                args: [packlotlines]
//                                                })
//                                        line.price_manually_set = true;
//                                        line.set_unit_price(price[1]);
//                                    }
//                                }
                            }
                 }
                 else{
                        this.props.resolve({ confirmed: true, payload: await this.getPayload() });
                        this.trigger('close-popup');
                 }

            }

        };

    Registries.Component.extend(EditListPopup, PosEditlistpopup);

    return EditListPopup;




});



