# -*- coding: utf-8 -*-
{
    'name': "om_recovery_reporting",

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
    'depends': ['jelly_mobilization','lease_reporting'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'reports/recovery_report_print_pdf.xml',
        'reports/installment_receipt_print_pdf.xml',
        'views/views.xml',
        'views/templates.xml',
        'wizard/recovery_report_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
