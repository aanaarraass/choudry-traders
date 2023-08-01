# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _


from odoo.exceptions import ValidationError


class Relation(models.Model):
    _name = 'relation'

    name = fields.Char()


class LeaseSale(models.Model):
    _name = 'lease.sale'
    _description = 'Lease Sale Agreement'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']


    name = fields.Char(
        'Lease ID', copy=False, default=lambda self: _('New'),
        required=True ,tracking=True, )
    partner_id = fields.Many2one('res.partner', string='Customer',tracking=True,)
    state = fields.Selection([('draft', 'Draft'), ('pending', 'In Process'),
                              ('done', 'Approved'),('return', 'Sale Return')],default='draft',tracking=True,)
    branch_id = fields.Many2one('res.branch',tracking=True,)
    ref_person = fields.Char('Reference Person',tracking=True,)
    ref_relation_id = fields.Many2one('relation', string='Relation',tracking=True,)
    lease_sale_item_ids = fields.One2many('lease.sale.item', 'lease_sale_id')
    lease_sale_return_ids = fields.One2many('lease.sale.return', 'lease_sale_id')
    account_no = fields.Char('Account No',tracking=True,)
    lease_date = fields.Date(string='Lease Date',tracking=True,)
    instalment_date = fields.Date('Instalment Date',tracking=True,)

    # cheque Detail
    account_holder_name = fields.Char('Account Holder Name',tracking=True,)
    father_name = fields.Char('Father Name',tracking=True,)
    relation_id = fields.Many2one('relation',tracking=True,)
    phone = fields.Char('Phone No',tracking=True,)
    bank_id = fields.Many2one('res.bank',tracking=True,)
    cheque_1 = fields.Char('Cheque No 1',tracking=True,)
    cheque_2 = fields.Char('Cheque No 2',tracking=True,)
    inquiry_officer = fields.Many2one('res.users',tracking=True,)
    branch_manger_id = fields.Many2one('res.users',tracking=True,)
    stock_incharge_id = fields.Many2one('res.users',tracking=True,)
    auditor_id = fields.Many2one('res.users',tracking=True,)
    customer_catgory = fields.Selection([('low', 'Low'), ('moderate', 'Moderate'),
                                         ('high', 'High')],default='low', string='Customer Catgory',tracking=True,)
    visit_date = fields.Date('Visit Date',tracking=True,)
    comments = fields.Text('Comments',tracking=True,)

    installment_ids = fields.One2many('lease.sale.instalment', 'lease_sale_id')

    picking_count = fields.Integer(string='Picking', compute='count_lease_sale')
    number_of_instalment = fields.Integer('Number Of Instalment',tracking=True,)
    guarantor_ids = fields.Many2many('guarantor',tracking=True,)
    invoice_count = fields.Integer(compute='count_invoice',tracking=True,)

    advance_payment_ids = fields.Many2many('account.move',tracking=True,)

    sale_total = fields.Float('Sale Total',compute='com_sale_total',tracking=True,)
    sale_return_total = fields.Float('Sale Return Total',compute='com_sale_total',tracking=True,)


    def sale_return(self):
        self.state = 'return'

    def cancel_sale_return(self):
        self.state = 'done'

    def re_schedule_instalment_plan(self):
        if self.number_of_instalment <= 0:
            raise ValidationError ('Number Of Instalment Must Greater Than Zero.')
        if not self.instalment_date:
            raise ValidationError ('Please Input Instatlment Date')
        if not self.lease_sale_return_ids:
            raise ValidationError ('Please Select Return Product')
        for instalment in self.installment_ids:
            if not instalment.invoice_id:
                instalment.unlink()
            else:
                pass

        advance = self.advance_payment_ids.amount_total_signed
        posted_invoice = sum(self.installment_ids.filtered(lambda x:x.invoice_id.state=='posted').mapped('invoice_id.amount_total_signed'))
        total_sale = self.sale_total
        total_sale_return = self.sale_return_total

        net_sale = total_sale -total_sale_return
        total_received= advance+posted_invoice
        remaining = net_sale-total_received
        number_of_instalment = self.number_of_instalment
        instalment_date = self.instalment_date
        due_date = instalment_date
        instalment_amount = remaining / number_of_instalment

        insatlment_number = 1
        for i in range(1, number_of_instalment + 1):
            reference = 'Reschedule Instalment %s' % insatlment_number
            instalment_id = self.env['lease.sale.instalment'].create({
                'name': reference,
                'due_date': due_date,
                'amount': instalment_amount,
                'lease_sale_id': self.id
            })
            if i == number_of_instalment:
                break
            next_month_date = due_date + relativedelta(months=1)
            if due_date.day > next_month_date.day:
                next_month_date -= relativedelta(days=due_date.day - next_month_date.day)
            due_date = next_month_date
            insatlment_number += 1



    def com_sale_total(self):
        for rec in self:
            rec.sale_total = 0
            rec.sale_return_total = 0
            for line in rec.lease_sale_item_ids:
                rec.sale_total+=line.total
            for return_line in rec.lease_sale_return_ids:
                rec.sale_return_total +=return_line.total


    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError ('You Can Not Delete Lease Record.')
        return super().unlink()

    def count_invoice(self):
        self.invoice_count = len(self.installment_ids.invoice_id)


    def count_lease_sale(self):
        self.picking_count = self.env['stock.picking'].search_count([('lease_sale_id', '=', self.id)])

    def action_view_lease_sale(self):
        return {
            'name': _('Delivery'),
            'view_mode': 'tree,form',
            'domain': [('lease_sale_id', '=', self.id)],
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'active_test': False},
        }

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('lease.sale') or _('New')
        res = super(LeaseSale, self).create(vals)

        return res

    def approve_state(self):
        self.state = 'done'
        if not self.branch_id:
            raise ValidationError ('Please Select Branch')
        if self.picking_count == 0:
            self.prepare_delivery()

    def create_instalment_plan(self):
        if self.number_of_instalment <= 0:
            raise ValidationError ('Number Of Instalment Must Greater Than Zero.')
        if not self.instalment_date:
            raise ValidationError ('Please Input Instatlment Date')
        if not self.lease_sale_item_ids:
            raise ValidationError ('Please Select Product')
        self.state = 'pending'
        for instalment in self.installment_ids:
            if not instalment.invoice_id:
                instalment.unlink()
            else:
                pass
        # self.installment_ids = False
        total = sum(item.total for item in self.lease_sale_item_ids)
        number_of_instalment = self.number_of_instalment
        advance = sum(adv.amount_total_signed for adv in self.advance_payment_ids)
        instalment_date = self.instalment_date
        total_for_instalment = total - advance
        instalment_amount = total_for_instalment / number_of_instalment
        # r = np.remainder(total_for_instalment, number_of_instalment)
        # a = np.round(instalment_amount)
        due_date = instalment_date
        insatlment_number = 1
        for i in range(1, number_of_instalment + 1):
            reference = 'Instalment %s' % insatlment_number
            instalment_id = self.env['lease.sale.instalment'].create({
                'name': reference,
                'due_date': due_date,
                'amount': instalment_amount,
                'lease_sale_id': self.id
            })
            if i == number_of_instalment:
                break
            next_month_date = due_date + relativedelta(months=1)
            if due_date.day > next_month_date.day:
                next_month_date -= relativedelta(days=due_date.day - next_month_date.day)
            due_date = next_month_date
            insatlment_number += 1

    def prepare_vals(self):
        warehouse_id = self.env['stock.warehouse'].search([('branch_id', '=', self.branch_id.id)], limit=1)
        picking_type_id = self.env['stock.picking.type'].search([('warehouse_id', '=', warehouse_id.id),
                                                                 ('code', '=', 'outgoing'),
                                                                 ('name', '=', 'Delivery Orders')], limit=1)
        vals = {
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'branch_id': self.branch_id.id,
            'picking_type_id': picking_type_id.id,
            'location_id': picking_type_id.default_location_src_id.id,
            'location_dest_id': picking_type_id.default_location_dest_id.id,
            'lease_sale_id': self.id,
        }
        return vals

    def stock_move(self, picking_id):
        for item in self.lease_sale_item_ids:
            stock_move = self.env['stock.move'].create({
                'reference': picking_id.name,
                'name': picking_id.name,
                'location_id': picking_id.location_id.id,
                'location_dest_id': picking_id.location_dest_id.id,
                'product_id': item.product_id.id,
                'branch_id': picking_id.branch_id.id,
                'product_uom_qty': item.qty,
                'product_uom': item.product_id.uom_id.id,
                'origin': item.lease_sale_id.name,
                'picking_id': picking_id.id
            })
        return True

    def prepare_delivery(self):
        picking = self.env['stock.picking']
        vals = self.prepare_vals()
        picking_id = picking.create(vals)
        stock_move = self.stock_move(picking_id)


    def reset(self):
        self.state = 'draft'

    def view_invoices(self):
        invoice_ids =list(id.invoice_id.id for id in self.installment_ids)
        return {
            'name': _('Invoices'),
            'view_mode': 'tree,form',
            'domain': [('id', 'in', invoice_ids)],
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'active_test': False},
        }

class leaseSaleItem(models.Model):
    _name = 'lease.sale.item'
    _description = 'Lease Sale Product'

    product_id = fields.Many2one('product.product', string='Item Name')
    qty = fields.Float('Quantity',default=1)
    price = fields.Float('Unit Price')
    total = fields.Float('Amount', compute='calculate_total')
    lease_sale_id = fields.Many2one('lease.sale')
    lease_sale_return_id = fields.Many2one('lease.sale.return')

    @api.onchange('qty', 'price', 'product_id')
    def calculate_total(self):
        for rec in self:
            rec.price = rec.product_id.list_price
            rec.total = rec.price * rec.qty

    def return_product(self):
        view_id = self.env.ref('cybat_installment_sale.lease_sale_return_wizard_action')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Return Product'),
            'view_mode': 'form',
            'res_model': 'lease.sale.return.wizard',
            'target': 'new',
        }





class leaseSaleReturn(models.Model):
    _name = 'lease.sale.return'
    _description = 'Lease Sale Return'

    product_id = fields.Many2one('product.product', string='Item Name')
    qty = fields.Float('Quantity',default=1)
    price = fields.Float('Unit Price')
    total = fields.Float('Amount', compute='calculate_total')
    lease_sale_id = fields.Many2one('lease.sale')

    @api.onchange('qty', 'price', 'product_id')
    def calculate_total(self):
        for rec in self:
            rec.total = rec.price * rec.qty


class leaseSaleReturnWizard(models.TransientModel):
    _name = 'lease.sale.return.wizard'
    _description = 'Lease Sale Return Wizard'

    product_id = fields.Many2one('product.product', string='Item Name')
    qty = fields.Float('Quantity',default=1)
    price = fields.Float('Unit Price')
    total = fields.Float('Amount')
    lease_sale_id = fields.Many2one('lease.sale')

    @api.model
    def default_get(self, fields):
        result = super(leaseSaleReturnWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        sale_line = self.env['lease.sale.item'].browse(active_id)
        result['product_id'] = sale_line.product_id.id
        result['qty'] = sale_line.qty
        result['price'] = sale_line.price
        return result

    def return_product(self):
        active_id = self.env.context.get('active_id')
        sale_line = self.env['lease.sale.item'].browse(active_id)
        if self.qty > sale_line.qty:
            raise ValidationError ('Return Quantity Is Greater Than Sale Quantity.')
        if self.price > sale_line.price:
            raise ValidationError ('Return Price Is Greater Than Sale Price.')
        if not sale_line.lease_sale_return_id:
            lease_sale_return = self.env['lease.sale.return'].create({
                'product_id':self.product_id.id,
                'qty':self.qty,
                'price':self.price,
                'lease_sale_id':sale_line.lease_sale_id.id
            })
            sale_line.lease_sale_return_id = lease_sale_return.id

        else:
            sale_line.lease_sale_return_id.qty = self.qty
            sale_line.lease_sale_return_id.price = self.price










class LeaseSaleInstalment(models.Model):
    _name = 'lease.sale.instalment'
    _description = 'Lease Sale Installment Line'

    name = fields.Char('Reference')
    due_date = fields.Date(string='Instalment Date')
    amount = fields.Float('Amount')

    lease_sale_id = fields.Many2one('lease.sale')
    invoice_id = fields.Many2one('account.move')
    invoice_status = fields.Selection(related='invoice_id.state',)
    invoice_payment_status = fields.Selection(related='invoice_id.payment_state',)
    discount_total = fields.Monetary(related='invoice_id.discount_total')
    amount_paid = fields.Monetary(related='invoice_id.amount_total_signed')
    currency_id = fields.Many2one('res.currency')

    def prepare_invoice_vals(self):
        product = self.env['product.product'].search([('name', '=', self.name)], limit=1)
        if product:
            product_id = product
        else:
            product_id = self.env['product.product'].create({'name': self.name, 'detailed_type': 'service'})
        invoice_vals = {
            'ref': '%s %s' % (self.lease_sale_id.name, self.name),
            'move_type': 'out_invoice',
            'invoice_user_id': self.env.user.id,
            'invoice_date_due': self.due_date,
            'invoice_date': self.due_date,
            'partner_id': self.lease_sale_id.partner_id.id,
            'payment_reference': '%s %s' % (self.lease_sale_id.name, self.name),
            'is_instalment': True,
            'instalment_id':self.id,
            'invoice_line_ids': [(0, 0, {
                'name': product_id.name,
                'price_unit': self.amount,
                'quantity': 1.0,
                'product_id': product_id.id,
            })],
        }
        return invoice_vals

    def create_invoice(self):
        if not self.invoice_id:
            vals = self.prepare_invoice_vals()
            invoice_id = self.env['account.move'].create(vals)
            self.invoice_id = invoice_id.id
            self.invoice_id.action_post()
        else:
            raise ValidationError ('Invoice Already Created.')
        return True





class StockPricking(models.Model):
    _inherit = 'stock.picking'

    lease_sale_id = fields.Many2one('lease.sale')



class AccountMove(models.Model):
    _inherit = 'account.move'

    is_instalment = fields.Boolean()
    instalment_id = fields.Many2one('lease.sale.instalment')

    discount_total = fields.Monetary("Discount Total", compute='total_discount')

    # Count the total discount
    @api.depends('invoice_line_ids.quantity', 'invoice_line_ids.price_unit', 'invoice_line_ids.discount')
    def total_discount(self):
        for invoice in self:
            total_price = 0
            discount_amount = 0
            final_discount_amount = 0
            if invoice:
                for line in invoice.invoice_line_ids:
                    if line:
                        total_price = line.quantity * line.price_unit
                        if total_price:
                            discount_amount = total_price - line.price_subtotal
                            if discount_amount:
                                final_discount_amount = final_discount_amount + discount_amount
                invoice.update({'discount_total': final_discount_amount})

