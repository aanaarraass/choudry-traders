from odoo import models, fields


class InstallmentsReceiptsDetails(models.TransientModel):
    _name = 'installment.receipts.details'
    _description = "This model is being used to get data on wizard"

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    def installment_receipts(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        return self.env.ref('lease_reporting.installment_receipts_details_reports_ids').report_action(self, data=data)
