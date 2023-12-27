from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import models, fields
import datetime


class MonthlyClosingReport(models.TransientModel):
    _name = 'monthly.closing.report'
    _description = "This model is being used to get data on month wise closing Report"
    # _rec_name = 'branch_id'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    # branch_id = fields.Many2one('res.branch')

    def monthly_closing_report_print(self):
        next_12_months = [(self.date_from + relativedelta(months=i)).strftime('%b %Y') for i in range(0, 12)]
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'next_12_months': next_12_months,
            # 'branch_id': self.branch_id.id,
        }
        return self.env.ref('monthly_closing_report.monthly_closing_report_pdf_action').report_action(self, data=data)