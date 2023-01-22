odoo.define('matager_shop_modifier.saleorder_return', function (require) {
'use strict';

    var website_sale = require('website_sale.website_sale');
    var portalDetails = require('portal.portal');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    var QWeb = core.qweb;
    var _t = core._t;


    publicWidget.registry.sale_order_return = publicWidget.Widget.extend({
        selector : '#sidebar_content',

        events: {
            'click .o_return_btn': '_return_sale_order',
        },



    //   method to get address_search on type on field
    _return_sale_order: function (ev) {
        debugger;
        var self = this;
        ajax.rpc('/sale/return/portal', {
                    token:ev.currentTarget.value,
                    }).then(async function (response)
                    {
                        location.reload();
                    })
        },




   });
});


