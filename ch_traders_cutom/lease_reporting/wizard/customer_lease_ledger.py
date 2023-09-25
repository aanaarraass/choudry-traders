from odoo import models, fields
from odoo.exceptions import ValidationError


class CnicWiseReport(models.TransientModel):
    _name = 'cnic.wise.report'
    _description = "This model is being used to get data on wizard"
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string="Name")
    cnic = fields.Char(string="Cnic")

    def get_cnic_through_qty(self):
        if self.partner_id:
            recs = self.env['lease.sale'].search([('partner_id', '=', self.partner_id.id)])
        else:
            cnic = self.env['res.partner'].search([('cnic','=',self.cnic)],limit=1)
            recs = self.env['lease.sale'].search([('partner_id', '=', cnic.id)])
        if not recs:
            raise ValidationError("Customer Not Found.")
        id_list = []
        for rec in recs:
            id_list.append(rec.id)

        data = {
            'id_list': id_list,
        }
        return self.env.ref('lease_reporting.search_though_cnic_customer_ledger').report_action(self, data=data)
