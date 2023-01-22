odoo.define('matager_account_modifier.address_search', function (require) {
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
    var interval;

    //    Hide address suggestion div on scroll
    $(document).ready(function()
    {
        $('#wrapwrap').scroll(function(){
        $('.pac-container').hide()
        });
    });

    publicWidget.registry.websiteAddress = publicWidget.Widget.extend({
        selector : '.checkout_autoformat',

        events: {
            'keypress input[name="street"]': 'get_address',
            'keyup input[name="phone"]': 'validate_phone',
            'keyup input[name="email"]': 'validate_email',
            'change input[name="phone"]': 'validate_phone_alert',
            'change input[name="email"]': 'validate_email_alert',
            'click .shop_address_phone_verify': 'phone_number_send_otp',
            'click .shop_address_email_verify': 'email_send_otp',
            'click .modal_phone_verify_submit': 'validate_phone_number_otp',
            'click .modal_email_verify_submit': 'validate_email_otp',
            'click .btn_resend_otp_phone': 'resend_phone_otp',
            'click .btn_resend_otp_email': 'resend_email_otp',
        },

    //  start function to load map
    init: function()
    {
        this._super.apply(this, arguments);
        var self = this;
        if (typeof google== 'undefined') {
            window.ginit = self.on_ready;
            ajax.rpc('/get/googleapikey', {
                model: 'ir.config_parameter',
                domain: [['key','=','google_maps_api_key']],
            }).then(function (results) {
                if (results.length) {
                    self.google_maps_api_key = results;
                } else {
                    alert("Please add google_maps_api_key parameter with Google Map API Key value in system parameters.");
                }
            }).then(function (){
                $.getScript("https://maps.googleapis.com/maps/api/js?key="+self.google_maps_api_key+"&libraries=places");
            });
        }
        else{
            self.on_ready();
        }
        return true;
    },

    startTimer :function (duration, display) {

    var start = Date.now(),
        diff,
        minutes,
        seconds;
    function timer() {
        // get the number of seconds that have elapsed since
        // startTimer() was called
        diff = duration - (((Date.now() - start) / 1000) | 0);

        // does the same job as parseInt truncates the float
        minutes = (diff / 60) | 0;
        seconds = (diff % 60) | 0;

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (diff <= 0) {
            // if time is finish show error

            display.textContent = "OTP Expired!!";
        }
    };
    // we don't want to wait a full second before the timer starts
    timer();
    interval = setInterval(timer, 1000);
},

    otp_remaining_timer : function (ev,timer) {
      var timeleft = parseFloat(timer);
      timer = 60 * timeleft;

     if (ev.currentTarget.classList.contains('shop_address_phone_verify') || ev.currentTarget.classList.contains('btn_resend_otp_phone')){
           document.getElementById("countdown_phone").textContent = ""
            this.startTimer(timer,document.getElementById("countdown_phone"))
      }
      else{
             document.getElementById("countdown_email").textContent = ""
      this.startTimer(timer,document.getElementById("countdown_email"))
      }
},


    _placeChanged: function (autocomplete, input)
    {
        var place = autocomplete.getPlace();
        var self =this;
        this._updateAddress({
            input: input,
            address_components: place.address_components
        });
    },

    //   set data to field in shop address fields
    _updateAddress : function (args)
    {
        var $city = $(args.input.parentElement.parentElement).find("input[name='city']");
        var $country = $(args.input.parentElement.parentElement).find("#country_id");
        var $state = $(args.input.parentElement.parentElement).find("#state_id");

        $city.val('');
        $country.val('');
        $state.val('');

        var country = '';
        var state = '';
        var state_long_name = '';
        var route = '';
        if (args.address_components != undefined)
        {
            for (var i = 0; i < args.address_components.length; i++) {
                var component = args.address_components[i];
                var addressType = component.types[0];
                switch (addressType) {
                    case 'locality':
                        $city.val(component.long_name);
                        break;
                    case 'administrative_area_level_1':
                        state = component.short_name;
                        state_long_name = component.long_name;
                        break;
                    case 'country':
                        country = component.short_name;
                        break;
                }
            }
    //        call rpc to get id of state and country
             ajax.rpc('/map/data/response', {
                    country:country,
                    state:state,
                    state_long_name:state_long_name
                    })
                    .then(async function (response)
                    {
                       if (response)
                       {
                          if(response.country_id)
                          {
                            $('select[name="country_id"]').val(response.country_id.id)
                            $('select[name="state_id"]').empty();
                            ajax.jsonRpc('/country/get_state', 'call',
                                {
                                'country_id' : response.country_id.id,
                                }).then(function (result)
                                {
                                    $('select[name="state_id"]').append( $("<option>").val('').html('state...'));
                                    $('.div_state').hide()
                                    $('#div_state').hide()
                                    for (var i = 0; i < result.length; i++)
                                    {
                                        $('.div_state').show()
                                        $('#div_state').show()
                                        $('select[name="state_id"]').append( $("<option>").val(result[i]['id']).html(result[i]['name']));
                                    }
                                    $('select[name="state_id"]').val(response.state_id.id)

                                });
                          }
                          else
                           {
                                $('select[name="country_id"]').val('');
                                $('select[name="state_id"]').val('');
                           }
                       }
                    });
        }
    },

    //   method to get address_search on type on field
    get_address: function (ev)
    {
        var self =this;
        var input = ev.currentTarget
        var autocomplete = new google.maps.places.Autocomplete(input);
        let div_address = $('.pac-container')
        for (var i = 1; i < div_address.length; i++)
        {
           div_address[i].remove()
        }
         autocomplete.addListener('place_changed', function () {
         self._placeChanged(autocomplete, input);
        });

        },

    // Validate phone on  write data in filed
    validate_phone : function(evt)
    {
        var temp = evt.target.value
        $(evt.target).removeClass('red_phone');
        $(evt.target).removeClass('green_phone');
        let phone_number = temp;
        let reg = /([\d]{8})/;
        let matches = phone_number.match(reg);
        if (matches && matches.length>0 && temp.length == 8)
        {
            $(evt.target).addClass('green_phone');
        }
        else if(temp.length < 8 )
        {
            $(evt.target).addClass('red_phone');
        }
        else
        {
            $(evt.target).addClass('red_phone');
        }

    },

    // Validate Email on  write data in filed
    validate_email : function(evt)
    {
        var temp = evt.target.value
        $(evt.target).removeClass('red_phone');
        $(evt.target).removeClass('green_phone');
        let email = temp;
        let reg = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        let matches = reg.test(email);
        if (reg.test(email))
        {
            $(evt.target).addClass('green_phone');
        }
        else
        {
            $(evt.target).addClass('red_phone');
        }
    },

    // Validate phone on  change of  filed
    validate_phone_alert : function(evt)
    {
        if ($('input[name="phone"]').val()){
         ajax.rpc('/web/shop/address/change/phone', {
         'change_phone':$('input[name="phone"]').val(),
         'phone_verify_field':$('input[name="phone_verify_field"]').val(),
         'phone_verify_checkbox':$('input[name="phone_verify_checkbox"]').prop( "checked" ),
         'partner':$('input[name="partner_id"]').val()
         }).then(function (result) {
         if (result.show == true){
            $('#phone_verify_checkbox').prop('checked', false);
            if ($('.shop_address_phone_verify_main').length >0){
            $('.shop_address_phone_verify_main').show()
            }
            else{
            $('input[name="phone"]').after(result.phone_render_template)
            }
            }
          else{
            $('#phone_verify_checkbox').prop('checked', true);
            $('.shop_address_phone_verify_main').hide()
            }
            });
            }

        var temp = evt.target.value
        let phone_number = temp;
        let reg = /([\d]{8})/;
        let matches = phone_number.match(reg);
         if (matches && matches.length>0 && temp.length == 8)
         {
            $('.field_shop_address_phone').html('')
           return true;
         }
        else if(temp.length < 8)
        {
           $('.field_shop_address_phone').html('<p class="alert alert-danger field_shop_address_phone_error" role="alert">Please Enter Correct Phone Number !</p>')
        }
        else
        {
            $('.field_shop_address_phone').html('<p class="alert alert-danger field_shop_address_phone_error" role="alert">Please Enter Correct Phone Number !</p>')
        }
    },

    // Validate email on  Change of  filed
    validate_email_alert : function(evt)
    {
    if ($('input[name="email"]').val()){
         ajax.rpc('/web/shop/address/change/email', {
         'change_email':$('input[name="email"]').val(),
         'email_verify_checkbox':$('input[name="email_verify_checkbox"]').prop( "checked" ),
         'email_verify_field':$('input[name="email_verify_field"]').val(),
         'partner':$('input[name="partner_id"]').val()
         }).then(function (result) {
         if (result.show == true){
            $('#email_verify_checkbox').prop('checked', false);
            if ($('.shop_address_email_main').length >0){
            $('.shop_address_email_main').show()
            }
            else{
            $('input[name="email"]').after(result.email_render_template)
            }
            }
          else{
            $('#email_verify_checkbox').prop('checked', true);
            $('.shop_address_email_main').hide()
            }
            });
            }
        var temp = evt.target.value
        let email = temp;
        let reg = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        let matches = reg.test(email);
        if (reg.test(email)==false)
        {
           $('.field_shop_address_email').html('<p class="alert alert-danger field_shop_address_email_error" role="alert">Please Enter Correct Email !</p>')
        }
        else
        {
           $('.field_shop_address_email').html('')
        }
    },

    validate_phone_number_otp: function(ev)
    {
      ajax.rpc('/web/shop/address/phone/otp/verify/submit', {
        'phone_verify' : $(ev.delegateTarget).find('input[name="phone_verify_shop_address"]').val(),
        'partner' : $(ev.delegateTarget).find('input[name="partner_id"]').val(),
        }).then(function (result)
        {
        $('.field_shop_address_otp_verify').html('')
        if (result.phone_otp_expire == true){
        $('.field_shop_address_otp_verify').html('<p class="alert alert-danger field_shop_address_otp_verify_error" role="alert">Your OTP is Expire please resend OTP!</p>')
        }
        else if (result.phone_verify == false ){
        $('.field_shop_address_otp_verify').html('<p class="alert alert-danger field_shop_address_otp_verify_error" role="alert">Invalid Code !</p>')
        }
        else{
        $('#phone_verify_checkbox').prop('checked', true);
        $('#phone_verify_field').val($(ev.delegateTarget).find('input[name="phone"]').val());
        $('.shop_address_phone_verify_main').hide()
        $('#modal_phone_verify').modal('hide')
        }
      });
    },

    resend_phone_otp : function(ev)
    {
    var self = this;
    self.phone_number_send_otp(ev)
    },
    resend_email_otp : function(ev)
    {
    var self = this;
    self.email_send_otp(ev)
    },
    validate_email_otp: function(ev)
    {
      ajax.rpc('/web/shop/address/email/otp/verify/submit', {
        'email_verify' : $(ev.delegateTarget).find('input[name="email_verify_shop_address"]').val(),
        }).then(function (result)
        {
        $('.field_email_address_otp_verify').html('')
        if (result.email_otp_expire == true){
        $('.field_email_address_otp_verify').html('<p class="alert alert-danger field_email_shop_address_otp_verify_error" role="alert">Your OTP is Expire please resend OTP!</p>')
        }
        else if (result.email_verify == false ){
        $('.field_email_address_otp_verify').html('<p class="alert alert-danger field_email_shop_address_otp_verify_error" role="alert">Invalid Code !</p>')
        }
        else{
        $('#email_verify_checkbox').prop('checked', true);
        $('#email_verify_field').val($(ev.delegateTarget).find('input[name="email"]').val());
        $('.shop_address_email_main').hide()
        $('#modal_email_verify').modal('hide')
        }
      });
    },

    phone_number_send_otp: function(ev)
    {
      var self = this;
      ajax.rpc('/web/shop/address/phone/verify/send/otp', {
        'phone' : $(ev.delegateTarget).find('input[name="phone"]').val(),
        'partner':$('input[name="partner_id"]').val(),
        }).then(function (result)
        {
        $('.field_shop_address_phone').html('')
        if (result.not_user_error == true ){
        $('.field_shop_address_phone').html('<p class="alert alert-danger field_shop_address_phone_verify_error" role="alert">Already register with same phone number !</p>')
        }
        if (result.not_user_error == false ){
            clearInterval(interval);
            debugger;
           self.otp_remaining_timer(ev,result.timer);
           $('.field_shop_address_otp_verify').html("")
           $('#phone_verify_shop_address').val("")
           $('#modal_phone_verify').modal('show')
        }
        if (result.not_phone == true ){
        $('.field_shop_address_phone').html('<p class="alert alert-danger field_shop_address_phone_verify_error" role="alert">Please enter phone number!</p>')
        }
        if (result.in_correct_phone_number == true ){
        $('.field_shop_address_phone').html('<p class="alert alert-danger field_shop_address_phone_verify_error" role="alert">Please enter correct phone number!</p>')
        }
      });
    },

    email_send_otp: function(ev)
    {
    var self = this;
      if ($(ev.delegateTarget).find('input[name="name"]').val() != ''){
      $('.otp_name_required').html('')
      ajax.rpc('/web/shop/address/email/verify/send/otp', {
        'email' : $(ev.delegateTarget).find('input[name="email"]').val(),
        'name' : $(ev.delegateTarget).find('input[name="name"]').val(),
        'partner' : $(ev.delegateTarget).find('input[name="partner_id"]').val(),
        }).then(function (result)
        {

        $('.field_shop_address_email').html('')
        if (result.not_user_error == true ){
        $('.field_shop_address_email').html('<p class="alert alert-danger field_shop_address_email_verify_error" role="alert">Already register with same Email!</p>')
        }
        if (result.not_user_error == false ){
            clearInterval(interval);
            self.otp_remaining_timer(ev,result.timer);
           $('.field_email_address_otp_verify').html("")
           $('#email_verify_shop_address').val("")
           $('#modal_email_verify').modal('show')
        }
        if (result.not_email == true ){
        $('.field_shop_address_email').html('<p class="alert alert-danger field_shop_address_email_verify_error" role="alert">Please enter Email!</p>')
        }
        if (result.in_correct_email == true ){
        $('.field_shop_address_email').html('<p class="alert alert-danger field_shop_address_email_verify_error" role="alert">Please enter correct email!</p>')
        }
      });

    }
    else{
    $('.otp_name_required').html('<p class="alert alert-danger field_otp_name_required_error" role="alert">Please enter name to validate email!</p>')
    }
    },

   });
});


