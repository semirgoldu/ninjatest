odoo.define('taqat_pos_extended.models', function (require) {
"use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    var _super_order = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function (attributes, options) {
                var self = this;
                var res = _super_order.initialize.apply(this, arguments);
            },
        init_from_JSON: function (json) {
            this.visa_number = this.visa_number ? this.order.visa_number : '';
            _super_order.init_from_JSON.apply(this, arguments);
        },
        export_as_JSON: function() {
           var result = _super_order.export_as_JSON.apply(this, arguments);
           result.visa_number = this.visa_number;
           return result;
        },
        export_for_printing: function() {
          var result = _super_order.export_for_printing.apply(this,arguments);
          result.visa_number = this.visa_number
          return result
        }
	});
});
