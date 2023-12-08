from datetime import timedelta
from odoo import models, fields


class RecoveryReport(models.TransientModel):
    _name = 'recovery.report'
    _description = "This model is being used to get data on wizard Recovery Report"

    portfolio_id = fields.Many2one('branch.portfolio', string='Portfolio')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    # branch_id = fields.Many2one('your.branch.model', string='Branch')
    # account_no = fields.Char(string='Account Number')

    def recovery_report_print(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'portfolio_id': self.portfolio_id.id,
        }
        lease_total = self.env['lease.sale'].search_count(
            [('portfolio_id', '=', self.portfolio_id.id), ('lease_date', '>=', self.date_from),('lease_date','<=',self.date_to)])
        data['lease_total']=lease_total
        return self.env.ref('om_recovery_reporting.recovery_report_pdf_action').report_action(self, data=data)
