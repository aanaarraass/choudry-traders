# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sweden - Accounting Reports',
    'icon': '/l10n_se/static/description/icon.png',
    'version': '1.0',
    'category': 'Accounting/Localizations/Reporting',
    'author': "XCLUDE, Linserv, Odoo SA",
    'description': """
        Accounting reports for Sweden
    """,
    'depends': [
        'l10n_se', 'account_reports'
    ],
    'data': [
        'data/account_financial_html_report_K3_bs_data.xml',
        'data/account_financial_html_report_K3_pnl_data.xml',
        'views/report_export_template.xml',
    ],
    'installable': True,
    'auto_install': True,
    'website': 'https://www.jtstorm.com/app/accounting',
    'license': 'OEEL-1',
}
