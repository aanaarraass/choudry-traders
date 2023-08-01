from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class RejectReason(models.TransientModel):
    _name = 'reject.reason'

    name = fields.Char('Reject Reason')

    def mark_reject(self):
        active_model = self._context.get('active_model')
        if active_model == 'guarantor':
            active_id = self.env.context.get("active_id")
            guarantor = self.env['guarantor'].browse(active_id)
            guarantor.comment = self.name
            guarantor.state = 'reject'
        if active_model == 'res.partner':
            active_id = self.env.context.get("active_id")
            guarantor = self.env['res.partner'].browse(active_id)
            guarantor.comment = self.name
            guarantor.state = 'reject'
        return True



class AdvancePayment(models.TransientModel):
    _name = 'lease.sale.advance.payment'


    amount = fields.Float('Amount')



    def register_payment(self):
        active_id = self.env.context.get("active_id")
        partner = self.env['res.partner'].browse(active_id)
        product = self.env['product.product'].search([('name', '=', 'Advance Payment')], limit=1)
        if product:
            product_id = product
        else:
            product_id = self.env['product.product'].create({'name': 'Advance Payment',
                                                             'detailed_type': 'service',
                                                             'taxes_id':False,
                                                             })
        invoice_vals = {
            'ref': '%s %s' % (partner.name, 'Advance Payment'),
            'move_type': 'out_invoice',
            'invoice_user_id': self.env.user.id,
            'invoice_date_due': fields.date.today(),
            'invoice_date': fields.date.today(),
            'partner_id': partner.id,
            'payment_reference': '%s %s' % (partner.name, 'Advance Payment'),
            'invoice_line_ids': [(0, 0, {
                'name': product_id.name,
                'price_unit': self.amount,
                'quantity': 1.0,
                'product_id': product_id.id,
            })],
        }
        invoice_id = self.env['account.move'].create(invoice_vals)
        invoice_id.action_post()
        partner.advance_paymeny_id = invoice_id.id