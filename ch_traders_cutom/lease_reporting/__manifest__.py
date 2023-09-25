# -*- coding: utf-8 -*-
{
    'name': "lease_reporting",

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
    'depends': ['cybat_installment_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'reports/lease_ledger.xml',
        'reports/lease_transection.xml',
        'reports/lease_branch_wise_summar.xml',
        'reports/lease_officer_wise_sale_summary.xml',
        'reports/officer_wise_over_due_summary.xml',
        'reports/lease_summary_month_wise.xml',
        'reports/lease_summary_year_wise.xml',
        'reports/lease_ledger_through_cnic.xml',
        'reports/installments_receipts_details_report.xml',
        'wizard/lease_transection_wizard.xml',
        'wizard/customer_lease_ledger.xml',
        'wizard/installment_receipts_details.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
