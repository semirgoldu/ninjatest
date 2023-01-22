odoo.define('matager_account_modifier.phone_email_timer', function(require) {
    "use strict";


    var website_sale = require('website_sale.website_sale');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    var QWeb = core.qweb;
    var _t = core._t;
    var interval ;
     publicWidget.registry.websitePhoneEmailTimer = publicWidget.Widget.extend({
        selector : '.otp_timer',
         init: function(ev)
        {
        this._super.apply(this, arguments);
        var self = this;
        ajax.rpc('/get/otp/timer', {
                 }).then(function (results) {
           self.otp_remaining_timer(ev,results.timer);
           });
        },

       startTimer :function (duration, display)
       {

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

     if ((ev.el.childNodes[1].querySelector('otp_timer') != null && (ev.el.childNodes[1].querySelector('.otp_timer').classList.contains('oe_signup_form_phone_verification') || ev.el.childNodes[1].querySelector('.otp_timer').classList.contains('btn_resend_otp_phone'))) || (ev.el.querySelector('.otp_timer') != null && (ev.el.querySelector('.otp_timer').classList.contains('oe_signup_form_phone_verification') || ev.el.querySelector('.otp_timer').classList.contains('btn_resend_otp_phone')))){
           document.getElementById("countdown_phone_signup").textContent = ""
           this.startTimer(timer,document.getElementById("countdown_phone_signup"))
      }
      else{
           document.getElementById("countdown_email_signup").textContent = ""
      this.startTimer(timer,document.getElementById("countdown_email_signup"))
      }
},


});
});

