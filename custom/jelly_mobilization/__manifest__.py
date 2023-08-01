# -*- coding: utf-8 -*-
{
    'name': "jelly_mobilization",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'branch', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/sms_history.xml',
        'views/seq.xml',
        'wizard/send_message.xml',
        'wizard/report_wizard_view.xml',
        'wizard/mobliztion_report.xml',
        'views/area.xml',
        'views/portfolio.xml',
        'views/res_user.xml',
        'views/sms_body.xml',
        'views/templates.xml',
        'views/views.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
