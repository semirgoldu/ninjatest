odoo.define('matager_account_modifier.phone_email_number_format_signup', function(require) {
    "use strict";


    var website_sale = require('website_sale.website_sale');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    var QWeb = core.qweb;
    var _t = core._t;
     publicWidget.registry.websitePhoneNumberSignup= publicWidget.Widget.extend({
        selector : '.oe_website_login_container',

        events: {
            'keyup input[name="phone"]': 'validate_phone',
            'keyup input[name="login"]': 'validate_email',
            'change input[name="phone"]': 'validate_phone_alert',
            'change input[name="login"]': 'validate_email_alert',
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

    // Validate Email on write data in filed
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

    // Validate phone on change of  filed
    validate_phone_alert : function(evt)
    {
        var temp = evt.target.value
        let phone_number = temp;
        let reg = /([\d]{8})/;
        let matches = phone_number.match(reg);

         if (matches && matches.length>0 && temp.length == 8)
         {
           $('.field_signup_phone').html('')
           return true;
         }
         else if(temp.length < 8 )
         {
            $('.field_signup_phone').html('<p class="alert alert-danger field_signup_phone_error" role="alert">Please Enter Correct Phone Number !</p>')
         }
         else
         {
            $('.field_signup_phone').html('<p class="alert alert-danger field_signup_phone_error" role="alert">Please Enter Correct Phone Number !</p>')
         }
    },

     // Validate email on change of  filed
    validate_email_alert : function(evt)
    {
        var temp = evt.target.value
        let email = temp;
        let reg = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        if (reg.test(email)==false)
        {
           $('.field_signup_email').html('<p class="alert alert-danger field_signup_email_error" role="alert">Please Enter Correct Email !</p>')
        }
        else
        {
        $('.field_signup_email').html('')
        }
    },

});
});

