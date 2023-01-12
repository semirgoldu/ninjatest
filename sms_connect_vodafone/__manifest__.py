
{
    'name': 'Sms Connect Vodafone',
    'version': '15.0.1.0',
    'category': 'Extras',
    'description': """ 
  An application to send sms using the sms connect vodafone sms gateway. 
  """,
    'author': 'Rimes Gold',
    'depends': [
        'base',
        'contacts'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menus.xml',
        'views/res_config_settings.xml',
        'views/sms_connect_source.xml',
        #'views/res_partner.xml',
        'views/sms_connect_sms.xml'

    ],
    'application':True,
    'installable' :True,

}
