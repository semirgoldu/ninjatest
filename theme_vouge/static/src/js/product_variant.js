odoo.define('product_reference_generator_bizople.sale_product', function(require) {

    $(document).ready(function() {
        var ajax = require('web.ajax');
        var rpc = require('web.rpc');
        var core = require('web.core');
        var publicWidget = require('web.public.widget');
        require('website_sale.website_sale');
        var _t = core._t;
        publicWidget.registry.WebsiteSale.include({
        	onChangeVariant: function (ev) {
                this._super.apply(this, arguments);
                var $parent = $(ev.target).closest('.js_product');
                var qty = $parent.find('input[name="add_qty"]').val();
                var combination = this.getSelectedVariantValues($parent);
                var parentCombination = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').parent_combination;
                var productTemplateId = parseInt($parent.find('.product_template_id').val());
                return ajax.jsonRpc('/product_code/get_combination_info', 'call', {
                    'product_template_id': productTemplateId,
                    'product_id': this._getProductId($parent),
                    'combination': combination,
                    'add_qty': parseInt(qty),
                    'pricelist_id': this.pricelistId || false,
                    'parent_combination': parentCombination,
                }).then(function (data) {
                    if (data){
                        $('.product_internal_reference').html(data)
                        $('.product_internal_reference').removeClass('d-none');
                    } else {
                        $('.product_internal_reference').addClass('d-none');
                    }
                    // $('.product_ref_code').html(data)
                });

            }
        })    
    })
})

// ajax cart modal js start

odoo.define('theme_vouge.ajax_cart', function(require) {
    "use strict";
    var ajax = require('web.ajax');
    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    require('website_sale.website_sale');
    var timeout;
    var _t = core._t;

    publicWidget.registry.WebsiteSale.include({
        _onClickSubmit: function (ev, forceSubmit) {
            if ($(ev.currentTarget).is('#add_to_cart,.o_wsale_product_btn:not(.config_cart_btn) .a-submit') && !forceSubmit) {
                return;
            }

            var $aSubmit = $(ev.currentTarget);
            if (!ev.isDefaultPrevented() && !$aSubmit.is(".disabled")) {
                ev.preventDefault();
                if ($aSubmit.parents('.ajax_cart_modal_tools').length) {
                    var frm = $aSubmit.closest('form');
                    var product_product = frm.find('input[name="product_id"]').val();
                    var quantity = frm.find('.quantity').val();
                    if(!quantity) {
                       quantity = 1;
                    }
                    ajax.jsonRpc('/shop/cart/update_custom', 'call',{'product_id':product_product,'add_qty':quantity}).then(function(data) {
                        if(data) {
                            var $quantity = $(".my_cart_quantity");
                            var old_quantity = $quantity.html();
                            $quantity.parent().parent().removeClass('d-none');
                            $quantity.html(parseInt(quantity) + parseInt(old_quantity)).hide().fadeIn(600);
                        }
                    });
                    $(".select-modal-backdrop").remove();
                    $(".select-modal").remove();
                    $(".quick-modal-backdrop").remove();
                    $(".quick-modal").remove();
                } else {
                    $aSubmit.closest('form').submit();
                }
            }
            if ($aSubmit.hasClass('a-submit-disable')){
                $aSubmit.addClass("disabled");
            }
            if ($aSubmit.hasClass('a-submit-loading')){
                var loading = '<span class="fa fa-cog fa-spin"/>';
                var fa_span = $aSubmit.find('span[class*="fa"]');
                if (fa_span.length){
                    fa_span.replaceWith(loading);
                } else {
                    $aSubmit.append(loading);
                }
            }
        },
    });
});

// ajax cart modal js ends