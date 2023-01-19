



odoo.define('ebs_product_extend.widget_body_map', function (require) {
    "use strict";

var core = require('web.core');
var QWeb = core.qweb;
var field_utils = require("web.field_utils")
var session = require('web.session');
var rpc = require('web.rpc')
var widgetRegistry = require('web.widget_registry');
var Widget = require('web.Widget');
var ajax = require('web.ajax');
var cameraStream = null;
// var xml_load = ajax.loadXML(
//        '/taqat_webcam/static/src/xml/webcam.xml',
//        QWeb
//    );





var body_map = Widget.extend({
	template: 'body_map_view',
	events:{
	'click .attachment_web_cam':'_open_webcam',
	'click .capture_image':'_capture_image',
	'click .save_image':'_save_image',
	},

	 init: function (parent, action) {
        this._super.apply(this, arguments);
    var html_content = QWeb.render('image_open_template',{})
    $('#stream').remove()
     $('#capture').remove()
     $('#snapshot').remove()
    $('div.o_DialogManager').after(html_content);
    var self = this;
    $('.capture_image').on('click',self._capture_image.bind(self))
    $('.save_image').on('click',self._save_image.bind(self))
    $('.close_popup').on('click',self._close_popup.bind(self))
    },


    _stop_camera: function (){
        if( null != cameraStream ) {

            var track = cameraStream.getTracks()[ 0 ];

            track.stop();
            stream.load();

            cameraStream = null;
        }

    },


    _close_popup: function (ev){
        this._stop_camera();
		$('#open_webcam').modal('hide');
    },

    _save_image: function (ev){
        var image = $('.image_data').val()
        var id = this.__parentedParent.state.data.id
        var model = this.__parentedParent.state.model
        console.log("---this-image",image,this,model,id)
        this._rpc({
            model: 'donation.order',
            method: 'get_web_cam_image',
            args: [id],
            kwargs: {

                image: image,
                model: model,
            },
        }),
        this._stop_camera();
		$('#open_webcam').modal('hide')

    },



    _capture_image: function (ev){
    if( null != cameraStream ) {

		var ctx = capture.getContext( '2d' );
		var img = new Image();

		ctx.drawImage( stream, 0, 0, capture.width, capture.height );

		$('.image_data').val(capture.toDataURL( "image/png" ).split(',')[1])

		img.src	= capture.toDataURL("image/png" );
		img.width = 200;
		img.height = 180;

		snapshot.innerHTML = '';

		snapshot.appendChild( img );
		$('.save_image').show();
//		this._stop_camera();
//		$('#open_webcam').modal('hide')
	}

    },



    _open_webcam: function (ev){
    console.log("====================eeeeeeeeeeeeeeeeeee");
    $('#open_webcam').modal('show')
    $('.save_image').hide();
    var mediaSupport = 'mediaDevices' in navigator;

	if( mediaSupport && null == cameraStream ) {

		navigator.mediaDevices.getUserMedia( { video: { width: 320,
                height: 240,
                dest_width: 320,
                dest_height: 240,
                image_format: 'jpeg',
                jpeg_quality: 100,
                force_flash: true,
                fps: 30, facingMode: "environment" } } )
		.then( function( mediaStream ) {
		var video = document.getElementById('stream');
            video.setAttribute('autoplay', '');
            video.setAttribute('muted', '');
            video.setAttribute('playsinline', '');


			cameraStream = mediaStream;

			stream.srcObject = mediaStream;

			stream.play();
		})
		.catch( function( err ) {

			console.log( "Unable to access camera: " + err );
		});
	}
	else {

		alert( 'Your browser does not support media devices.' );

		return;
	}
    },

});

widgetRegistry.add("body_map", body_map)

});
