# -*- coding: utf-8 -*-
{
    'name': "cyb_payroll",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "aces",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Salary',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_attendance', 'hr_payroll_community','hr_holidays'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'wizard/hr_payslip_wizard.xml',

        'views/views.xml',
        'views/incentive_view.xml',
        'views/hr_payslip.xml',
        'views/resource_calendar_inherit.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
