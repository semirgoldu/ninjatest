$(document).ready(function(){
    
    $(function() {
      $('#wrapwrap').scroll(function() {
        if ($(this).scrollTop() > 100) {
          $('a.top').addClass('show-to-top');
        } else {
          $('a.top').removeClass('show-to-top');
        }
      });
      $('#to-top a').click(function() {
        $('body,html').animate({
          scrollTop : 0
        }, 800);
        return false;
      });
    });

    $(function() {
      $('#wrapwrap').scroll(function() {
        if ($(this).scrollTop() > 100) {
          $('.bizople-mbl-bottom-bar').addClass('show-bottom-bar');
        } else {
          $('.bizople-mbl-bottom-bar').removeClass('show-bottom-bar');
        }
      });
    });
   
    $("a.active").find('.mycheckbox').prop('checked', true);
    
    // Price slider code start
    var minval = $("input#m1").attr('value'),
        maxval = $('input#m2').attr('value'),
        minrange = $('input#ra1').attr('value'),
        maxrange = $('input#ra2').attr('value'),
        website_currency = $('input#vouge_website_currency').attr('value');
    if (!minval) {
        minval = 0;
    }
    if (!maxval) {
        maxval = maxrange;
    }
    if (!minrange) {
        minrange = 0;

    }
    if (!maxrange) {
        maxrange = 2000;
    }

    $("div#priceslider").ionRangeSlider({
        keyboard: true,
        min: parseInt(minrange),
        max: parseInt(maxrange),
        type: 'double',
        from: minval,
        skin: "square",
        to: maxval,
        step: 1,
        prefix: website_currency,
        grid: true,
        onFinish: function(data) {
            $("input[name='min1']").attr('value', parseInt(data.from));
            $("input[name='max1']").attr('value', parseInt(data.to));
            $("div#priceslider").closest("form").submit();
        },
    });

    $('[data-toggle="popover"]').popover()

	$('body').on('click', function (e) {
	    $('[data-toggle=popover]').each(function () {
	        // hide any open popovers when the anywhere else in the body is clicked
	        if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
	            $(this).popover('hide');
	        }
	    });
	});

    $(".close-search").click(function() {
      $(".search-box").removeClass("open");
    });


    if($('.template_404_page').hasClass('template_404_page')){
      $('.template_404_page').parent().siblings('hr').addClass('d-none');
    }
});

/* Close select modal when add to cart popup opens (start) */


function CloseCartSidebar() {
  $(".blured-bg").removeClass("active");
  $("#cart_sidebar").removeClass("toggled");
  $(".similar-sidebar-content").removeClass("toggled");
}

/* Close select modal when add to cart popup opens (end) */

$(function() {

  $("body").addClass("blured-bg");

  /* menu sidebar js */
  $("#show-sidebar").on("click", function(e) {
    $(".sidebar-wrapper").parents(".blured-bg").addClass("active");
    $(".sidebar-wrapper").addClass("toggled");
    e.stopPropagation()
  });
  $(".bottom-show-sidebar").on("click", function(e) {
    $(".sidebar-wrapper").parents(".blured-bg").addClass("active");
    $(".sidebar-wrapper").addClass("toggled");
    e.stopPropagation()
  });
  $("#close_mbl_sidebar").on("click", function(e) {
    $(".sidebar-wrapper").parents(".blured-bg").removeClass("active");
    $(".sidebar-wrapper").removeClass("toggled");
    e.stopPropagation()
  });
  $(document).on("click", function(e) {
    if (!$(e.target).closest('.sidebar-wrapper').length) {
      $(".sidebar-wrapper.toggled").parents(".blured-bg").removeClass("active");
      $(".sidebar-wrapper").removeClass("toggled");
    }
  });


  /* cart sidebar js */


  $(document).on("click", function(e) {
    if (!$(e.target).closest('#cart_sidebar').length) {
      $("#cart_sidebar.toggled").parents(".blured-bg").removeClass("active");
      $("#cart_sidebar").removeClass("toggled");
    }
  });

  /* category sidebar js */
  $(".filter_btn").on("click", function(e) {
    $("category-sidebar").parents(".blured-bg").addClass("active");
    $(".category-sidebar").addClass("toggled");
    e.stopPropagation()
  });
  $(".bottom_bar_filter_button").on("click", function(e) {
    $("category-sidebar").parents(".blured-bg").addClass("active");
    $(".category-sidebar").addClass("toggled");
    e.stopPropagation()
  });
  $("#category_close").on("click", function(e) {
    $("category-sidebar").parents(".blured-bg").removeClass("active");
    $(".category-sidebar").removeClass("toggled");
    e.stopPropagation()
  });
  $(document).on("click", function(e) {
    if (!$(e.target).closest('.category-sidebar').length) {
      $(".category-sidebar.toggled").parents(".blured-bg").removeClass("active");
      $(".category-sidebar").removeClass("toggled");
    }
    if (!$(e.target).closest('.similar-sidebar-content').length) {
      $(".similar-sidebar-content.toggled").parents(".blured-bg").removeClass("active");
      $(".similar-sidebar-content").removeClass("toggled");
    }
    if (!$(e.target).closest('.bizople-search-results').length) {
      $(".bizople-search-results").hide("dropdown-menu");
    }
    if (!$(e.target).closest('.bizople-search-text').length) {
      $(".bizople-search-text").hide("dropdown-menu");
    }
  });
  $("#categbtn-popup,#categbtn").on("click", function(e) {
    $(".bizople-search-results").hide("dropdown-menu");
    $(".bizople-search-text").hide("dropdown-menu");
  });


});



/* header category menu --- submenu*/
$(function() {
    var categ_target = $(".vouge-header-category > li.dropdown-submenu > .nav-link > i.ti");
    var parent_categ = $(categ_target).parent().parent();
    if ($(categ_target).hasClass("ti")) {
        $(parent_categ).addClass('dropright');
    }
});

/* shop page grid */
function grid4(){
    if ($(".vouge_product_pager .o_wsale_apply_layout .grid4").hasClass("active")) {
      $(".vouge_shop #products_grid").removeClass("sale_layout_grid4");
    }else {
      $(".vouge_shop #products_grid").addClass("sale_layout_grid4");
      localStorage.setItem("class", "sale_layout_grid4");
      $(".vouge_shop #products_grid").removeClass("o_wsale_layout_list");
      $(".vouge_product_pager .o_wsale_apply_layout .sale_list").removeClass("active");
      $(".vouge_shop #products_grid").removeClass("sale_layout_grid3");
      $(".vouge_product_pager .o_wsale_apply_layout .grid3").removeClass("active");
      $(".vouge_shop #products_grid").removeClass("sale_layout_grid2");
      $(".vouge_product_pager .o_wsale_apply_layout .grid2").removeClass("active");
    }
};

function grid3(){
    if ($(".vouge_product_pager .o_wsale_apply_layout .grid3").hasClass("active")) {
      $(".vouge_shop #products_grid").removeClass("sale_layout_grid3");
    }else {
      $(".vouge_shop #products_grid").addClass("sale_layout_grid3");
      localStorage.setItem("class", "sale_layout_grid3");
      $(".vouge_shop #products_grid").removeClass("o_wsale_layout_list");
      $(".vouge_product_pager .o_wsale_apply_layout .sale_list").removeClass("active");
      $(".vouge_shop #products_grid").removeClass("sale_layout_grid4");
      $(".vouge_product_pager .o_wsale_apply_layout .grid4").removeClass("active");
      $(".vouge_shop #products_grid").removeClass("sale_layout_grid2");
      $(".vouge_product_pager .o_wsale_apply_layout .grid2").removeClass("active");
    }
};

function grid2(){
    if ($(".vouge_product_pager .o_wsale_apply_layout .grid2").hasClass("active")) {
      $(".vouge_shop #products_grid").removeClass("sale_layout_grid2");
    }else {
      $(".vouge_shop #products_grid").addClass("sale_layout_grid2");
      localStorage.setItem("class", "sale_layout_grid2");
      $(".vouge_shop #products_grid").removeClass("o_wsale_layout_list");
      $(".vouge_product_pager .o_wsale_apply_layout .sale_list").removeClass("active");
      $(".vouge_shop #products_grid").removeClass("sale_layout_grid4");
      $(".vouge_product_pager .o_wsale_apply_layout .grid4").removeClass("active");
      $(".vouge_shop #products_grid").removeClass("sale_layout_grid3");
      $(".vouge_product_pager .o_wsale_apply_layout .grid3").removeClass("active");
    }
};

function salelist(){
    if ($(".vouge_product_pager .o_wsale_apply_layout .sale_list").hasClass("active")) {
      $(".vouge_shop #products_grid").removeClass("o_wsale_layout_list");
    }else {
      $(".vouge_shop #products_grid").addClass("o_wsale_layout_list");
      localStorage.setItem("class", "o_wsale_layout_list");
      $(".vouge_shop #products_grid").removeClass("sale_layout_grid3");
      $(".vouge_product_pager .o_wsale_apply_layout .grid3").removeClass("active");
      $(".vouge_shop #products_grid").removeClass("sale_layout_grid4");
      $(".vouge_product_pager .o_wsale_apply_layout .grid4").removeClass("active");
      $(".vouge_shop #products_grid").removeClass("sale_layout_grid2");
      $(".vouge_product_pager .o_wsale_apply_layout .grid2").removeClass("active");
    }
};

function SetClass() {
//before assigning class check local storage if it has any value
    $(".vouge_shop #products_grid").addClass(localStorage.getItem("class"));
    ActiveClass();
}

function ActiveClass() {
    if ($(".vouge_shop #products_grid").hasClass("o_wsale_layout_list")) {
      $(".vouge_product_pager .o_wsale_apply_layout .sale_list").addClass("active");
    }else if ($(".vouge_shop #products_grid").hasClass("sale_layout_grid3"))  {
      $(".vouge_product_pager .o_wsale_apply_layout .grid3").addClass("active");
    }else if ($(".vouge_shop #products_grid").hasClass("sale_layout_grid4"))  {
      $(".vouge_product_pager .o_wsale_apply_layout .grid4").addClass("active");
    }else if ($(".vouge_shop #products_grid").hasClass("sale_layout_grid2"))  {
      $(".vouge_product_pager .o_wsale_apply_layout .grid2").addClass("active");
    }
}

$(function() {
    SetClass();
});

$(function() {
    if ( !$(".vouge_shop .vouge_product_pager .grid4").hasClass("active") && !$(".vouge_shop .vouge_product_pager .grid3").hasClass("active") && !$(".vouge_shop .vouge_product_pager .grid2").hasClass("active") && !$(".vouge_shop .vouge_product_pager .sale_list").hasClass("active")) {
      $(".vouge_shop .vouge_product_pager .grid4").addClass("active");
    }
});

$(function() {
    if ($('.vouge_shop').hasClass('vouge_shop')) {
      $('.bottom-bar-filter').removeClass('d-none');
      $('.bottom-bar-shop').addClass('d-none');
    }else {
      $('.bottom-bar-filter').addClass('d-none');
      $('.bottom-bar-shop').removeClass('d-none');
    }
});

if ($(".product_categ_description").height() > 110){
  $(".description_box .read-more").removeClass("d-none");
}

function categfade(){
  
  var $el, $ps, $up, totalHeight;

    totalHeight = 0

    $ps = $(".product_categ_description");

    
    // measure how tall inside should be by adding together heights of all inside paragraphs (except read-more paragraph)
    $ps.each(function() {
      totalHeight += $(this).outerHeight();
    });
          
    $(".description_box")
      .css({
        // Set height to prevent instant jumpdown when max height is removed
        "height": $(".description_box").height(),
        "max-height": 9999
      })
      .animate({
        "height": totalHeight
      });
    
    // fade out read-more
    $(".read-more").fadeOut();
    
    // prevent jump-down
    return false;
};


$(document).ready(function() {
 
  $("#vogue_categ_slider").owlCarousel({
 
      autoPlay: 3000, //Set AutoPlay to 3 seconds
      responsiveClass: true,
      items : 5,
      loop: false,
      center: false,
      margin: 0,
      nav:true,
      navText: [
          '<i class="fa fa-long-arrow-left" aria-hidden="true"></i>',
          '<i class="fa fa-long-arrow-right" aria-hidden="true"></i>'
      ],
      responsive: {
          0: {
              items: 2,
          },
          420: {
              items: 2,
          },
          768: {
              items: 3,
          },
          1024: {
              items: 5,
          },
          1200: {
              items: 5,
          },
          1400: {
              items: 5,
          },
      },
 
  });

  $("#vogue_sub_categ_slider").owlCarousel({
 
      autoPlay: 3000, //Set AutoPlay to 3 seconds
      responsiveClass: true,
      items : 4,
      loop: false,
      center: false,
      margin: 0,
      nav:true,
      navText: [
          '<i class="fa fa-long-arrow-left" aria-hidden="true"></i>',
          '<i class="fa fa-long-arrow-right" aria-hidden="true"></i>'
      ],
      responsive: {
        0: {
            items: 2,
        },
        420: {
            items: 2,
        },
        768: {
            items: 3,
        },
        1024: {
            items: 5,
        },
        1200: {
            items: 5,
        },
        1400: {
            items: 5,
        },
      },
  });
 
});

$(function(){
  var show_cart_link = $("header .bizople-add-to-cart .o_wsale_my_cart a");
  if ($('header > nav').hasClass("header-cart-sidebar")){
    show_cart_link.addClass('show_cart_sidebar');
    show_cart_link.removeAttr("href");
    show_cart_link.attr("role","button");
    show_cart_link.attr('onclick','show_cart()');
    show_cart();
  }else {
    show_cart_link.removeClass('show_cart_sidebar');
    show_cart_link.removeAttr("role");
    show_cart_link.attr("href","/shop/cart");
    show_cart_link.removeAttr('onclick','show_cart()');
  }
});

function show_cart(){
  $(".show_cart_sidebar").on("click", function(e) {
    $("#cart_sidebar").addClass("toggled");
    e.stopPropagation()
  });
  $("#close_cart_sidebar").on("click", function(e) {
    $("#cart_sidebar").removeClass("toggled");
    e.stopPropagation()
  });
}

odoo.define('theme_vouge.common', function(require){
'use strict';

  require('web.dom_ready');
  var publicWidget = require('web.public.widget');
  var core = require('web.core');
  var ajax = require('web.ajax');
  var rpc = require('web.rpc');
  var _t = core._t;


  var publicWidget = require('web.public.widget');

  publicWidget.registry.shoppagejs = publicWidget.Widget.extend({
    selector: ".vouge_shop",
    start: function () {
      $('.lazyload').lazyload();

      /* Product hover image js start */
      setInterval(function(){
        $(".product_extra_hover_image").hover(function(){
              var product_id = $(this).find('.has_extra_hover_image .extra_hover_image').attr('productid');
              var target_image = $(this).find('.has_extra_hover_image .extra_hover_image img');
              $(target_image).attr('data-src', '/web/image/product.template/' + product_id +'/hover_image');
              $('.lazyload').lazyload();
          }, function(){
              var target_image = $(this).find('.has_extra_hover_image .extra_hover_image img');
              $(target_image).delay(200).attr('data-src', ' ');
          });
        }, 1000);
      /* Product hover image js end */

    }
  });
  publicWidget.registry.productpage = publicWidget.Widget.extend({
    selector: "#product_detail",
    start: function () {
      setInterval(function(){
        $('.lazyload').lazyload();
      }, 1000);
    }
  });

});

function openSearchPopup() {
  $(".search-box").addClass("open");
}

function CartSidebar() {
  $("#cart_sidebar").addClass("toggled");
}