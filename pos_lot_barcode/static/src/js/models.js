odoo.define("pos_lot_barcode.models", function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var utils = require('web.utils');
    var round_di = utils.round_decimals;


    var _super_order = models.Orderline.prototype;
        models.Orderline = models.Orderline.extend({
	    initialize: function (attributes, options) {
            var self = this;
            var res = _super_order.initialize.apply(this, arguments);
        },
        can_be_merged_with: function(orderline){
            var price = parseFloat(round_di(this.price || 0, this.pos.dp['Product Price']).toFixed(this.pos.dp['Product Price']));
            var order_line_price = orderline.get_product().get_price(orderline.order.pricelist, this.get_quantity());
            order_line_price = round_di(orderline.compute_fixed_price(order_line_price), this.pos.currency.decimals);
            if( this.get_product().id !== orderline.get_product().id){    //only orderline of the same product can be merged
                return false;
            }else if(!this.get_unit() || !this.get_unit().is_pos_groupable){
                return false;
            }else if(this.get_discount() > 0){             // we don't merge discounted orderlines
                return false;
            }else if(!utils.float_is_zero(price - order_line_price - orderline.get_price_extra(),
                        this.pos.currency.decimals) && this.product.tracking == 'none'){
                return false;
            }else if(this.product.tracking == 'lot' && (this.pos.picking_type.use_create_lots || this.pos.picking_type.use_existing_lots)) {
                return false;
            }else if (this.description !== orderline.description) {
                return false;
            }else if (orderline.get_customer_note() !== this.get_customer_note()) {
                return false;
            } else if (this.refunded_orderline_id) {
                return false;
            }else{
                return true;
            }
        },
    })

})