odoo.define('taqat_pos_extended.getCustomer', function(require) {
    "use strict";

    var models = require('point_of_sale.models');

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function() {
            _super_order.initialize.apply(this, arguments);
            if (this.pos.config.default_customer_id && !this.export_as_JSON().partner_id) {
            	this.set_client(this.pos.db.get_partner_by_id(this.pos.config.default_customer_id[0]));
            }
        },
    });

    models.PosOrder = Backbone.Model.extend({
        initialize: function (session, attributes) {
            Backbone.Model.prototype.initialize.apply(this, arguments);
            this.visa_number = attributes.visa_number;
        },
    });
});