from datetime import timedelta
from odoo import models, fields


class RecoveryReport(models.TransientModel):
    _name = 'recovery.report'
    _description = "This model is being used to get data on wizard Recovery Report"
    _rec_name = 'branch_id'

    # portfolio_id = fields.Many2one('branch.portfolio', string='Portfolio')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    branch_id = fields.Many2one('res.branch')


    def recovery_report_print(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'branch_id': self.branch_id.id,
        }
        return self.env.ref('om_recovery_reporting.recovery_report_pdf_action').report_action(self, data=data)

    def installment_receipt_summary(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'branch_id': self.branch_id.id,
        }
        return self.env.ref('om_recovery_reporting.installment_receipt_pdf_action').report_action(self, data=data)
