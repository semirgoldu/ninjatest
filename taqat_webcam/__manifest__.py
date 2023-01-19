# -*- coding: utf-8 -*-
{
    'name': 'Webcam Module',
    'version': '15.0.0.1',
    'summary': 'WebCam module',
    'category': 'WebCam Widget',
    'author': 'TechUltra Solutions',
    'website': 'https://www.techultrasolutions.com/',
    'depends': ['base', ],
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            'taqat_webcam/static/src/js/webcam_widget.js',
            # 'taqat_webcam/static/src/css/main.css',

        ],
        'web.assets_qweb': [
            'taqat_webcam/static/src/xml/webcam.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
