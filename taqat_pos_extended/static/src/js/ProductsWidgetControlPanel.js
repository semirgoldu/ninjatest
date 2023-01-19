odoo.define("taqat_pos_extended.db", function (require) {
    "use strict";

    var PosDB = require("point_of_sale.DB");
    var models = require("point_of_sale.models");

    models.load_fields("product.product", ["lot_data_json"]);

    PosDB.include({
        _product_search_string: function (product) {
            var res = this._super(product).replace("\n", "");
            var lot_data_list = JSON.parse(product.lot_data_json);
            for (var i = 0, len = lot_data_list.length; i < len; i++) {
                var lot_data = lot_data_list[i];
                if (lot_data.lot_name) {
                    res += "|" + lot_data.lot_name.replace(/:/g, "");
                }
            }
            res += "\n";
            return res;
        },
    });
});