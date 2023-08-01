# -*- coding: utf-8 -*-
{
    'name': "JTS Fairo Otp",

    'summary': """
    this module created otp while login 
        """,

    'description': """
       
    """,

    'author': "My Company",
    'website': "https://jtstorm.com/",

    'category': '',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['web'],

    # always loaded
    'data': [
        'views/jts_res_user.xml',
        'views/web_address_inherit.xml',
        'views/web_login_inherit.xml',
        'views/web_otp_verification.xml',
    ],

}
