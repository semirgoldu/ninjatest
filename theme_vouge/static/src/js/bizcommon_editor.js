odoo.define('theme_vouge.bizcommon_editor_js', function(require) {
    'use strict';
    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;
    
    // ajax.loadXML('/theme_vouge/static/src/xml/bizople_theme_common.xml', qweb);
    // ajax.loadXML('/theme_vouge/static/src/xml/web_editor_inherit.xml', qweb);
    // ajax.loadXML('/theme_vouge/static/src/xml/button_editor.xml', qweb);   

    options.registry.config_slider_clone_fix = options.Class.extend({
        start: function() {
            var self = this;
            startinterval()
            function startinterval() {
                var id = setInterval(frame, 100);
                function frame() {
                    var targetbtn = $('.o_legacy_dialog .modal-footer > button.btn-primary')
                    if (targetbtn.length) {
                        clicksavebtn()
                        clearInterval(id);
                    }
                }
                function clicksavebtn() {
                    $('.o_legacy_dialog .modal-footer > button.btn-primary').on('click', function() {
                        $('.bizople_product_configurator').find('[class*=container]').empty();
                        $('.bizople_brand_configurator').find('[class*=container]').empty();
                        $('.bizople_category_configurator').find('[class*=container]').empty();
                    })
                }
            }
        },
    });

    options.registry.s_bizople_theme_blog_slider_snippet = options.Class.extend({
        xmlDependencies: ['/theme_vouge/static/src/xml/bizople_theme_common.xml'],
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.blog_slider_owl').empty();
            
            if (!editMode) {
                self.$el.find(".blog_slider_owl").on("click", _.bind(self.theme_vouge_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.theme_vouge_blog_slider()) {
                this.theme_vouge_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.blog_slider_owl').empty();
        },
        theme_vouge_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_vouge.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_vouge/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
});