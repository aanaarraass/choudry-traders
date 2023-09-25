# -*- coding: utf-8 -*-
from datetime import datetime, time, timedelta

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
        required=True, tracking=True, )
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=True, )
    state = fields.Selection([('draft', 'Draft'), ('pending', 'In Process'),
                              ('done', 'Running'), ('complete', 'Complete'), ('return', 'Sale Return')],
                             default='draft', tracking=True, )
    branch_id = fields.Many2one('res.branch', tracking=True, )
    ref_person = fields.Char('Reference Person', tracking=True, )
    ref_relation_id = fields.Many2one('relation', string='Relation', tracking=True, )
    lease_sale_item_ids = fields.One2many('lease.sale.item', 'lease_sale_id')
    lease_sale_return_ids = fields.One2many('lease.sale.return', 'lease_sale_id')
    account_no = fields.Char('Account No', tracking=True, )
    lease_date = fields.Date(string='Lease Date', tracking=True, )
    instalment_date = fields.Date('Instalment Date', tracking=True, )

    book_no = fields.Char(tracking=True,)
    form_no = fields.Char(tracking=True,)

    # cheque Detail
    account_holder_name = fields.Char('Account Holder Name', tracking=True, )
    father_name = fields.Char('Father Name', tracking=True, )
    relation_id = fields.Many2one('relation', tracking=True, )
    phone = fields.Char('Phone No', tracking=True, )
    bank_id = fields.Many2one('res.bank', tracking=True, )
    cheque_1 = fields.Char('Cheque No 1', tracking=True, )
    cheque_2 = fields.Char('Cheque No 2', tracking=True, )
    inquiry_officer = fields.Many2one('res.users', tracking=True, )
    branch_manger_id = fields.Many2one('res.users', tracking=True, )
    stock_incharge_id = fields.Many2one('res.users', tracking=True, )
    auditor_id = fields.Many2one('res.users', tracking=True, )
    customer_catgory = fields.Selection([('low', 'Low'), ('moderate', 'Moderate'),
                                         ('high', 'High')], default='low', string='Customer Catgory', tracking=True, )
    visit_date = fields.Date('Visit Date', tracking=True, )
    comments = fields.Text('Comments', tracking=True, )

    installment_ids = fields.One2many('lease.sale.instalment', 'lease_sale_id')

    picking_count = fields.Integer(string='Picking', compute='count_lease_sale')
    instalment_selection = fields.Selection([('number', 'No Of Instalment'), ('amount', 'Amount Of Instalment')
                                             ], string='Instalment Method', default='number')
    number_of_instalment = fields.Integer('Number Of Instalment', tracking=True, )
    amount_of_instalment = fields.Integer('Amount Of Instalment', tracking=True, )
    guarantor_ids = fields.Many2many('guarantor', tracking=True, )
    invoice_count = fields.Integer(compute='count_invoice', tracking=True, )

    advance_payment_ids = fields.Many2many('account.move', tracking=True, )

    sale_total = fields.Float('Sale Total', tracking=True, compute='calcualte_sale_After_discount')
    sale_return_total = fields.Float('Sale Return Total', compute='com_sale_total', tracking=True, )

    is_decesced = fields.Boolean('Deceased Customer', tracking=True, )
    is_defaulter = fields.Boolean('Defaulter Customer', tracking=True, )
    portfolio_id = fields.Many2one('branch.portfolio', tracking=True,)
    recovery_officer_id = fields.Many2one('hr.employee', tracking=True, )
    salesman_id = fields.Many2one('hr.employee', tracking=True, )

    sale_total_before_discount = fields.Float(compute='com_sale_total')
    discount_amount = fields.Float()
    discount_type = fields.Selection([('percent', 'Percent'), ('fixed', 'Fixed')], default='fixed')
    discount_percent = fields.Float()
    lease_sale_discount_invoice = fields.Many2one('account.move')
    total_paid = fields.Float(compute='compute_total_paid')
    total_receivable = fields.Float(compute='compute_total_paid')

    warning_message = fields.Text(compute='compute_warning_message')

    price_list_id = fields.Many2one('product.pricelist')


    @api.onchange('price_list_id','lease_sale_item_ids')
    def update_rate_in_sale_line(self):
        for rec in self.lease_sale_item_ids:
            if rec.lease_sale_id.price_list_id:
                product_price = rec.lease_sale_id.price_list_id.item_ids.filtered(lambda x:x.product_id.id == rec.product_id.id)
                if product_price:
                    if product_price.__len__() > 1:
                        list=[]
                        for p_list in product_price:
                            if p_list.date_start.date() >= rec.lease_sale_id.lease_date and p_list.date_end.date() >= rec.lease_sale_id.lease_date:
                                list.append(p_list)
                        if list.__len__() > 0:
                            rec.price = list[0].fixed_price
                        else:
                            rec.price = product_price[0].fixed_price
                    else:
                        rec.price = product_price.fixed_price
                else:
                    product_price = rec.lease_sale_id.price_list_id.item_ids.filtered(lambda x: x.product_tmpl_id.id == rec.product_id.product_tmpl_id.id)
                    if product_price:
                        if product_price.__len__() > 1:
                            list = []
                            for p_list in product_price:
                                if p_list.date_start.date() >= rec.lease_sale_id.lease_date and p_list.date_end.date() >= rec.lease_sale_id.lease_date:
                                    list.append(p_list)
                            if list.__len__() > 0:
                                rec.price = list[0].fixed_price
                            else:
                                rec.price = product_price[0].fixed_price
                        else:
                            rec.price = product_price.fixed_price
                    else:
                        rec.price = rec.product_id.list_price
            else:
                rec.price = rec.product_id.list_price



    def compute_warning_message(self):
        msg = ''
        if self.partner_id.state == 'draft':
            msg+="%s Verification Is Under Process " % (self.partner_id.name)
        if self.partner_id.state == 'reject':
            msg+="%s Verification Is Rejected " % (self.partner_id.name)
        self.warning_message = msg


    def compute_total_paid(self):
        for rec in self:
            total_paid = 0
            total_receivable = 0
            for line in rec.installment_ids:
                if line.invoice_id.payment_state == 'paid':
                    total_paid += line.invoice_id.amount_total_signed
                if line.invoice_id.payment_state != 'paid':
                    total_receivable += line.invoice_id.amount_total_signed
            rec.total_paid = total_paid
            rec.total_receivable = total_receivable

    def calcualte_sale_After_discount(self):
        for rec in self:
            rec.sale_total = rec.sale_total_before_discount - rec.discount_amount

    def sale_return(self):
        self.state = 'return'

    def cancel_sale_return(self):
        self.state = 'done'

    def lesase_status_complete(self):
        self.state = 'complete'

    def re_schedule_instalment_plan(self):
        if not self.instalment_date:
            raise ValidationError('Please Input Instatlment Date')
        if not self.lease_sale_item_ids:
            raise ValidationError('Please Select Product')
        self.state = 'done'
        for instalment in self.installment_ids:
            if not instalment.invoice_id:
                instalment.unlink()
            else:
                pass
        posted_invoice = sum(self.installment_ids.filtered(lambda x: x.invoice_id.state == 'posted').mapped(
            'invoice_id.amount_total_signed'))
        total_sale_return = self.sale_return_total
        # total = sum(item.total for item in self.lease_sale_item_ids)
        total = self.sale_total
        advance = sum(adv.amount_total_signed for adv in self.advance_payment_ids)
        total_for_instalment = total - advance - posted_invoice - total_sale_return
        if total_for_instalment < 0:
            return
        instalment_date = self.instalment_date
        due_date = instalment_date
        if self.instalment_selection == 'number':
            if self.number_of_instalment <= 0:
                raise ValidationError('Number Of Instalment Must Greater Than Zero.')
            number_of_instalment = self.number_of_instalment
            instalment_amount = total_for_instalment // number_of_instalment
            diffrence = total_for_instalment - (instalment_amount * number_of_instalment)
        elif self.instalment_selection == 'amount':
            if self.amount_of_instalment <= 0:
                raise ValidationError('Amount Of Instalment Must Greater Than Zero.')
            instalment_amount = self.amount_of_instalment
            number_of_instalment = int(total_for_instalment // instalment_amount)
            diffrence = total_for_instalment - (number_of_instalment * instalment_amount)
        else:
            raise ValidationError('Please Select Instalment Method.')
        for i in range(1, number_of_instalment + 1):
            if i == number_of_instalment:
                amount = instalment_amount + diffrence
            else:
                amount = instalment_amount
            reference = 'Re schedule Instalment %s' % i
            instalment_id = self.env['lease.sale.instalment'].create({
                'name': reference,
                'due_date': due_date,
                'amount': amount,
                'lease_sale_id': self.id
            })
            if i == number_of_instalment:
                break
            next_month_date = due_date + relativedelta(months=1)
            if due_date.day > next_month_date.day:
                next_month_date -= relativedelta(days=due_date.day - next_month_date.day)
            due_date = next_month_date

    def com_sale_total(self):
        for rec in self:
            rec.sale_total_before_discount = 0
            rec.sale_return_total = 0
            for line in rec.lease_sale_item_ids:
                rec.sale_total_before_discount += line.total
            for return_line in rec.lease_sale_return_ids:
                rec.sale_return_total += return_line.total

    @api.onchange('discount_percent')
    def calculate_discount(self):
        for rec in self:
            rec.discount_amount = (rec.discount_percent * rec.sale_total_before_discount) / 100

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError('You Can Not Delete Lease Record.')
        return super().unlink()

    def count_invoice(self):
        a = len(self.installment_ids.invoice_id)
        b = len(self.lease_sale_discount_invoice)
        self.invoice_count = a + b

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

    def view_advance_payment(self):
        list = [x.id for x in self.advance_payment_ids]
        return {
            'name': _('Advance Payment'),
            'view_mode': 'tree,form',
            'domain': [('id', 'in', list)],
            'res_model': 'account.move',
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
            raise ValidationError('Please Select Branch')
        if self.picking_count == 0:
            self.prepare_delivery()
        if self.partner_id.state == 'draft':
            self.partner_id.state = 'select'
        if not self.lease_sale_discount_invoice:
            if self.discount_amount > 0:
                self.calculate_discount_sale()
                self.lease_sale_discount_invoice.action_post()


    def calculate_discount_sale(self):
        discount_journal_id = int(self.env['ir.config_parameter'].search(
            [('key', '=', 'cybat_installment_sale.sale_discount_allowed_account_exp_id')]).value)
        sale_discount_allowed_account_id = int(self.env['ir.config_parameter'].search(
            [('key', '=', 'cybat_installment_sale.sale_discount_allowed_account_id')]).value)

        move_line_d = {
            'name': self.name,
            'partner_id': self.partner_id.id,
            'account_id': discount_journal_id,
            'debit': self.discount_amount,
            'credit': False,
        }
        move_line_c = {
            'name': self.name,
            'partner_id': self.partner_id.id,
            'account_id': sale_discount_allowed_account_id,
            'debit': False,
            'credit': self.discount_amount,
        }
        invoice_vals = {
            'ref': '%s %s' % (self.partner_id.name, self.name),
            'move_type': 'entry',
            'partner_id': self.partner_id.id,
            'date': fields.datetime.now(),
            'line_ids': [(0, 0, move_line_d), (0, 0, move_line_c)],
        }
        move = self.env['account.move'].create(invoice_vals)
        self.lease_sale_discount_invoice = move.id

    def create_instalment_plan(self):
        if not self.instalment_date:
            raise ValidationError('Please Input Installment Date')
        if not self.lease_sale_item_ids:
            raise ValidationError('Please Select Product')
        self.state = 'pending'
        for instalment in self.installment_ids:
            if not instalment.invoice_id:
                instalment.unlink()
            else:
                pass
        # total = sum(item.total for item in self.lease_sale_item_ids)
        total = self.sale_total
        advance = sum(adv.amount_total_signed for adv in self.advance_payment_ids)
        total_for_instalment = total - advance
        instalment_date = self.instalment_date
        due_date = instalment_date
        if self.instalment_selection == 'number':
            if self.number_of_instalment <= 0:
                raise ValidationError('Number Of Instalment Must Greater Than Zero.')
            number_of_instalment = self.number_of_instalment
            instalment_amount = total_for_instalment // number_of_instalment
            diffrence = total_for_instalment - (instalment_amount * number_of_instalment)
        elif self.instalment_selection == 'amount':
            if self.amount_of_instalment <= 0:
                raise ValidationError('Amount Of Instalment Must Greater Than Zero.')
            instalment_amount = self.amount_of_instalment
            number_of_instalment = int(total_for_instalment // instalment_amount)
            diffrence = total_for_instalment - (number_of_instalment * instalment_amount)
        else:
            raise ValidationError('Please Select Instalment Method.')
        for i in range(1, number_of_instalment + 1):
            if i == number_of_instalment:
                amount = instalment_amount + diffrence
            else:
                amount = instalment_amount
            reference = 'Instalment %s' % i
            instalment_id = self.env['lease.sale.instalment'].create({
                'name': reference,
                'due_date': due_date,
                'amount': amount,
                'lease_sale_id': self.id
            })
            if i == number_of_instalment:
                break
            next_month_date = due_date + relativedelta(months=1)
            if due_date.day > next_month_date.day:
                next_month_date -= relativedelta(days=due_date.day - next_month_date.day)
            due_date = next_month_date

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
        invoice_ids = list(id.invoice_id.id for id in self.installment_ids)
        if self.lease_sale_discount_invoice:
            invoice_ids.append(self.lease_sale_discount_invoice.id)
        return {
            'name': _('Invoices'),
            'view_mode': 'tree,form',
            'domain': [('id', 'in', invoice_ids)],
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'active_test': False},
        }

    def open_bad_debts_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Book Bad Debts/Settlement'),
            'view_mode': 'form',
            'res_model': 'bad.debts.wizard',
            'target': 'new',
        }

    def advance_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Advance Payment'),
            'view_mode': 'form',
            'res_model': 'lease.sale.advance.payment',
            'target': 'new',
            'res_id': False,
        }


class leaseSaleItem(models.Model):
    _name = 'lease.sale.item'
    _description = 'Lease Sale Product'
    _rec_name = 'lease_sale_id'

    product_id = fields.Many2one('product.product', string='Item Name')
    qty = fields.Float('Quantity', default=1)
    price = fields.Float('Unit Price')
    total = fields.Float('Amount', compute='calculate_total')
    lease_sale_id = fields.Many2one('lease.sale')
    lease_sale_return_id = fields.Many2one('lease.sale.return')

    @api.onchange('product_id')
    def calculate_price(self):
        for rec in self:
            if rec.lease_sale_id.price_list_id:
                product_price = rec.lease_sale_id.price_list_id.item_ids.filtered(lambda x:x.product_id.id == rec.product_id.id)
                if product_price:
                    if product_price.__len__() > 1:
                        list=[]
                        for p_list in product_price:
                            if p_list.date_start.date() >= rec.lease_sale_id.lease_date and p_list.date_end.date() >= rec.lease_sale_id.lease_date:
                                list.append(p_list)
                        if list.__len__() > 0:
                            rec.price = list[0].fixed_price
                        else:
                            rec.price = product_price[0].fixed_price
                    else:
                        rec.price = product_price.fixed_price
                else:
                    product_price = rec.lease_sale_id.price_list_id.item_ids.filtered(lambda x: x.product_tmpl_id.id == rec.product_id.product_tmpl_id.id)
                    if product_price.__len__() > 1:
                        list = []
                        for p_list in product_price:
                            if p_list.date_start.date() >= rec.lease_sale_id.lease_date and p_list.date_end.date() >= rec.lease_sale_id.lease_date:
                                list.append(p_list)
                        if list.__len__() > 0:
                            rec.price = list[0].fixed_price
                        else:
                            rec.price = product_price[0].fixed_price
                    else:
                        rec.price = product_price.fixed_price
            else:
                rec.price = rec.product_id.list_price

    @api.onchange('qty', 'price', 'product_id')
    def calculate_total(self):
        for rec in self:
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
    qty = fields.Float('Quantity', default=1)
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
    qty = fields.Float('Quantity', default=1)
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
            raise ValidationError('Return Quantity Is Greater Than Sale Quantity.')
        if self.price > sale_line.price:
            raise ValidationError('Return Price Is Greater Than Sale Price.')
        if not sale_line.lease_sale_return_id:
            lease_sale_return = self.env['lease.sale.return'].create({
                'product_id': self.product_id.id,
                'qty': self.qty,
                'price': self.price,
                'lease_sale_id': sale_line.lease_sale_id.id
            })
            sale_line.lease_sale_return_id = lease_sale_return.id

        else:
            sale_line.lease_sale_return_id.qty = self.qty
            sale_line.lease_sale_return_id.price = self.price


class BaddebetsWizard(models.TransientModel):
    _name = 'bad.debts.wizard'

    total_unpaid = fields.Float()
    is_full_pay = fields.Boolean()
    is_full_bad_debts = fields.Boolean()

    discount_type = fields.Selection([('fixed', 'Fixed'), ('percent', 'Percentage')], string='Discount Type',
                                     default='fixed')
    discount_amount = fields.Float('Discount')
    percent_discount = fields.Float('Percent')
    after_discount = fields.Float('Net Amount')
    reference = fields.Char('Write Off Label')

    @api.onchange('is_full_pay')
    def change_value_is_full(self):
        self.is_full_bad_debts = False

    @api.onchange('is_full_bad_debts')
    def change_value(self):
        self.is_full_pay = False

    @api.onchange('percent_discount')
    def calculate_discount(self):
        self.discount_amount = (self.percent_discount * self.total_unpaid) / 100

    @api.onchange('discount_amount')
    def calculate_net(self):
        self.after_discount = self.total_unpaid - self.discount_amount

    @api.model
    def default_get(self, fields):
        result = super(BaddebetsWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        lease_id = self.env['lease.sale'].search([('id', '=', active_id)])
        unpaid_invoice = sum(
            lease_id.installment_ids.filtered(lambda x: x.invoice_payment_status == 'not_paid').mapped('amount'))
        unpaid_instalment = sum(lease_id.installment_ids.filtered(lambda x: not x.invoice_id).mapped('amount'))
        is_bad_debts_line = sum(
            lease_id.installment_ids.filtered(lambda x: x.is_full_bad_debts == True).mapped('amount'))
        is_full_settlement_line = sum(
            lease_id.installment_ids.filtered(lambda x: x.is_full_settlement == True).mapped('amount'))
        total_of_unpaid = unpaid_invoice + unpaid_instalment - (is_full_settlement_line + is_bad_debts_line)
        result['total_unpaid'] = total_of_unpaid

        return result

    def create_bad_debts(self):
        active_id = self.env.context.get('active_id')
        lease_id = self.env['lease.sale'].search([('id', '=', active_id)])
        for rec in lease_id.installment_ids:
            if rec.is_full_settlement == True:
                if not rec.invoice_id:
                    rec.unlink()
                else:
                    raise ValidationError('Full Settlement Invoice Already Exists')
            elif rec.is_full_bad_debts == True:
                if not rec.invoice_id:
                    rec.unlink()
                else:
                    raise ValidationError('Write off Journal Entry Already Exists')
            else:
                pass
        if self.is_full_pay:
            unpaid_invoices = lease_id.installment_ids.filtered(lambda x: x.invoice_payment_status == 'not_paid')
            for line in unpaid_invoices:
                line.status = 'cancel'
                line.invoice_id.button_cancel()
            draft_instalments = lease_id.installment_ids.filtered(lambda x: not x.invoice_id)
            for instalment in draft_instalments:
                instalment.status = 'cancel'
            instalment_id = self.env['lease.sale.instalment'].create({
                'name': 'Full Settlement',
                'due_date': fields.date.today(),
                'amount': self.total_unpaid,
                'discount_type': self.discount_type,
                'percent_discount': self.percent_discount,
                'discount_amount': self.discount_amount,
                'is_full_settlement': True,
                'lease_sale_id': lease_id.id
            })
        if self.is_full_bad_debts:
            draft_instalments = lease_id.installment_ids.filtered(lambda x: not x.invoice_id)
            draft_invoice_cancel_instalments = lease_id.installment_ids.filtered(
                lambda x: x.invoice_id.payment_state == 'not_paid')
            if draft_instalments:
                for instalment in draft_instalments:
                    instalment.create_invoice()
            if draft_invoice_cancel_instalments:
                for cancel_invoice in draft_invoice_cancel_instalments:
                    cancel_invoice.invoice_id.button_draft()
                    cancel_invoice.invoice_id.action_post()
                    cancel_invoice.status = 'done'
            instalment_id = self.env['lease.sale.instalment'].create({
                'name': 'Write Off %s ( %s)' % (lease_id.partner_id.name, self.reference),
                'due_date': fields.date.today(),
                'amount': self.total_unpaid,
                'discount_amount': self.discount_amount,
                'is_full_bad_debts': True,
                'lease_sale_id': lease_id.id
            })


class LeaseSaleInstalment(models.Model):
    _name = 'lease.sale.instalment'
    _description = 'Lease Sale Installment Line'

    name = fields.Char('Reference')
    due_date = fields.Date(string='Instalment Date')
    amount = fields.Float('Amount')
    status = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')], default="draft")
    lease_sale_id = fields.Many2one('lease.sale')
    invoice_id = fields.Many2one('account.move')
    invoice_status = fields.Selection(related='invoice_id.state', )
    invoice_payment_status = fields.Selection(related='invoice_id.payment_state', )
    amount_paid = fields.Monetary(related='invoice_id.amount_total_signed')
    currency_id = fields.Many2one('res.currency')

    discount_type = fields.Selection([('fixed', 'Fixed'), ('percent', 'Percentage')], string='Discount Type',
                                     default='fixed')
    discount_amount = fields.Float('Discount')
    percent_discount = fields.Float('Percent')

    is_full_settlement = fields.Boolean()
    is_full_bad_debts = fields.Boolean()

    @api.onchange('percent_discount')
    def calculate_discount(self):
        self.discount_amount = (self.percent_discount * self.amount) / 100

    def cron_job_to_create_invoice(self):
        today = fields.date.today()
        to_day_instalment_draft = self.env['lease.sale.instalment'].search(
            [('status', '=', 'draft'), ('due_date', '=', today)])
        for instalment in to_day_instalment_draft:
            try:
                if not instalment.invoice_id:
                    instalment.create_invoice()
                else:
                    pass
            except:
                print('Cron job Failed to create Invoice')
        return True

    def prepare_invoice_vals(self):
        if self.is_full_bad_debts:
            bad_debts_account_id = int(self.env['ir.config_parameter'].search(
                [('key', '=', 'cybat_installment_sale.bed_debts_account_id')]).value)
            credit_account_id = int(self.lease_sale_id.partner_id.property_account_receivable_id.id)

            move_line_d = {
                'name': self.name,
                'partner_id': self.lease_sale_id.partner_id.id,
                'account_id': bad_debts_account_id,
                'debit': self.amount,
                'credit': False,
            }
            move_line_c = {
                'name': self.name,
                'partner_id': self.lease_sale_id.partner_id.id,
                'account_id': credit_account_id,
                'debit': False,
                'credit': self.amount,
            }

            invoice_vals = {
                'ref': '%s %s' % (self.lease_sale_id.name, self.name),
                'move_type': 'entry',
                'partner_id': self.lease_sale_id.partner_id.id,
                'date': fields.datetime.now(),
                'journal_id': 3,
                'line_ids': [(0, 0, move_line_d), (0, 0, move_line_c)],
            }
        else:
            product = self.env['product.product'].search([('name', '=', self.name)], limit=1)
            discount_product = self.env['product.product'].search([('name', '=', 'Instalment Discount')], limit=1)
            discount_journal_id = int(self.env['ir.config_parameter'].search(
                [('key', '=', 'cybat_installment_sale.instalment_discount_account_id')]).value)

            if discount_product:
                discount_product_id = discount_product
            else:
                discount_product_id = self.env['product.product'].create(
                    {'name': 'Instalment Discount', 'detailed_type': 'service',
                     'property_account_income_id': discount_journal_id})

            discount_amount = (self.discount_amount * -1)

            if product:
                product_id = product
            else:
                product_id = self.env['product.product'].create({'name': self.name, 'detailed_type': 'service'})

            if self.discount_amount > 0:
                line_ids = [(0, 0, {
                    'name': product_id.name,
                    'price_unit': self.amount,
                    'quantity': 1.0,
                    'product_id': product_id.id,
                }), (0, 0, {
                    'name': discount_product_id.name,
                    'price_unit': discount_amount,
                    'quantity': 1.0,
                    'tax_ids': False,
                    'product_id': discount_product_id.id,
                })]
            else:
                line_ids = [(0, 0, {
                    'name': product_id.name,
                    'price_unit': self.amount,
                    'quantity': 1.0,
                    'product_id': product_id.id,
                })]

            invoice_vals = {
                'ref': '%s %s' % (self.lease_sale_id.name, self.name),
                'move_type': 'out_invoice',
                'invoice_user_id': self.env.user.id,
                'invoice_date_due': self.due_date,
                'invoice_date': self.due_date,
                'partner_id': self.lease_sale_id.partner_id.id,
                'payment_reference': '%s %s' % (self.lease_sale_id.name, self.name),
                'is_instalment': True,
                'instalment_id': self.id,
                'invoice_line_ids': line_ids,
                'branch_id': self.lease_sale_id.branch_id.id,
                'portfolio_id':self.lease_sale_id.portfolio_id.id
            }
        return invoice_vals

    def create_invoice(self):
        if not self.invoice_id:
            vals = self.prepare_invoice_vals()
            invoice_id = self.env['account.move'].create(vals)
            self.invoice_id = invoice_id.id
            self.invoice_id.action_post()
            self.status = 'done'
        else:
            raise ValidationError('Invoice Already Created.')
        return True


class StockPricking(models.Model):
    _inherit = 'stock.picking'

    lease_sale_id = fields.Many2one('lease.sale')


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_instalment = fields.Boolean(copy=False)
    instalment_id = fields.Many2one('lease.sale.instalment', copy=False)
    portfolio_id = fields.Many2one('branch.portfolio',copy=False)




class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    instalment_discount_account_id = fields.Many2one('account.account',
                                                     help="Instalmenet Discount Account Which Pass Journal Entry ")
    bad_debts_account_id = fields.Many2one('account.account',
                                           help="Bed debts Settlement Account")
    sale_discount_allowed_account_id = fields.Many2one('account.account')
    sale_discount_allowed_account_exp_id = fields.Many2one('account.account')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['instalment_discount_account_id'] = int(
            self.env['ir.config_parameter'].sudo().get_param('cybat_installment_sale.instalment_discount_account_id'))
        res['bad_debts_account_id'] = int(
            self.env['ir.config_parameter'].sudo().get_param('cybat_installment_sale.bed_debts_account_id'))
        res['sale_discount_allowed_account_id'] = int(
            self.env['ir.config_parameter'].sudo().get_param('cybat_installment_sale.sale_discount_allowed_account_id'))
        res['sale_discount_allowed_account_exp_id'] = int(
            self.env['ir.config_parameter'].sudo().get_param(
                'cybat_installment_sale.sale_discount_allowed_account_exp_id'))
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('cybat_installment_sale.instalment_discount_account_id',
                                                         self.instalment_discount_account_id.id)
        self.env['ir.config_parameter'].sudo().set_param('cybat_installment_sale.bed_debts_account_id',
                                                         self.bad_debts_account_id.id)
        self.env['ir.config_parameter'].sudo().set_param('cybat_installment_sale.sale_discount_allowed_account_id',
                                                         self.sale_discount_allowed_account_id.id)
        self.env['ir.config_parameter'].sudo().set_param('cybat_installment_sale.sale_discount_allowed_account_exp_id',
                                                         self.sale_discount_allowed_account_exp_id.id)
        super(ResConfigSettings, self).set_values()


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payment_vals_from_wizard(self):
        vals = super()._create_payment_vals_from_wizard()
        if self.line_ids.move_id.is_instalment:
            vals.update({'is_instalment': self.line_ids.move_id.is_instalment})
            vals.update({'instalment_id': self.line_ids.move_id.instalment_id.id})
            vals.update({'recovery_officer_id': self.line_ids.move_id.portfolio_id.recovery_id.id})
            return vals
        else:
            return vals


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_instalment = fields.Boolean(copy=False)
    instalment_id = fields.Many2one('lease.sale.instalment', copy=False)
    recovery_officer_id = fields.Many2one('hr.employee')

