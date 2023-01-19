odoo.define('ebs_pos_extended.models', function (require) {
"use strict";

    var BarcodeParser = require('barcodes.BarcodeParser');
    var BarcodeReader = require('point_of_sale.BarcodeReader');
    var PosDB = require('point_of_sale.DB');
    var models = require('point_of_sale.models');
    var devices = require('point_of_sale.devices');
    var concurrency = require('web.concurrency');
    var config = require('web.config');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var time = require('web.time');
    var utils = require('web.utils');
    var QWeb = core.qweb;
    var _t = core._t;
    var Mutex = concurrency.Mutex;
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;
    var rpc = require('web.rpc');

    var exports = {};

    models.load_models({
            model: 'stock.production.lot',
            fields: ['id', 'name', 'product_id','price_unit', 'product_qty'],
            domain: [],
            loaded: function(self,lot_number) {
                self.lot_number = lot_number;
            }
        })

    var _super_order = models.Orderline.prototype;
	models.Orderline = models.Orderline.extend({
	    initialize: function (attributes, options) {
            var self = this;
            var res = _super_order.initialize.apply(this, arguments);
        },
        setPackLotLines: function({ modifiedPackLotLines, newPackLotLines }) {
            // Set the new values for modified lot lines.
            let lotLinesToRemove = [];
            for (let lotLine of this.pack_lot_lines.models) {
                const modifiedLotName = modifiedPackLotLines[lotLine.cid];
                if (modifiedLotName) {
                    lotLine.set({ lot_name: modifiedLotName });
                } else {
                    // We should not call lotLine.remove() here because
                    // we don't want to mutate the array while looping thru it.
                    lotLinesToRemove.push(lotLine);
                }
            }

            // Remove those that needed to be removed.
            for (let lotLine of lotLinesToRemove) {
                lotLine.remove();
            }

            // Create new pack lot lines.
            let newPackLotLine;
            for (let newLotLine of newPackLotLines) {
                newPackLotLine = new exports.Packlotline({}, { order_line: this });
                var lot = this.order.pos.lot_number.filter(p => p.name == newLotLine.lot_name);
                if(lot.length){
                    newPackLotLine.set({ lot_name: newLotLine.lot_name, price_unit: lot[0].price_unit });
                }
                else{
                    newPackLotLine.set({ lot_name: newLotLine.lot_name });
                }
                this.pack_lot_lines.add(newPackLotLine);
            }

            // Set the quantity of the line based on number of pack lots.
            if(!this.product.to_weight){
                this.pack_lot_lines.set_quantity_by_lot();
            }
        },
    })

    exports.Packlotline = Backbone.Model.extend({
        defaults: {
            lot_name: null,
            price_unit: 0.0
        },
        initialize: function(attributes, options){
            this.order_line = options.order_line;
            if (options.json) {
                this.init_from_JSON(options.json);
                return;
            }
        },

        init_from_JSON: function(json) {
            this.order_line = json.order_line;
            this.set_lot_name(json.lot_name);
            this.set_lot_price(json.price_unit);
        },

        set_lot_name: function(name){
            this.set({lot_name : _.str.trim(name) || null});
        },

        set_lot_price: function(price){
            this.set(price);
        },

        get_lot_name: function(){
            return this.get('lot_name');
        },

        get_lot_price: function(){
            return this.get('price_unit');
        },

        export_as_JSON: function(){
            return {
                lot_name: this.get_lot_name(),
                price_unit: this.get_lot_price(),
            };
        },

        add: function(){
            var order_line = this.order_line,
            index = this.collection.indexOf(this);
            var new_lot_model = new exports.Packlotline({}, {'order_line': this.order_line});
            this.collection.add(new_lot_model, {at: index + 1});
            return new_lot_model;
        },

        remove: function(){
            this.collection.remove(this);
        }
    });
});