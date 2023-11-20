# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MonthlyTarget(models.Model):
    _name = 'monthly.target'
    _description = 'Monthly Target'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(tracking=True)
    date_from = fields.Date(string='Date From',tracking=True)
    date_to = fields.Date(string='Date To',tracking=True)

    branch_target_ids = fields.One2many('branch.target','monthly_target_id',tracking=True)
    
    
    @api.onchange('branch_target_ids','name','date_from','date_to')
    def lines_update(self):
        for rec in self:
            for line in rec.branch_target_ids:
                line.date_from = rec.date_from
                line.date_to = rec.date_to
                line.name = rec.name


    def update_branches(self):
        branches = self.env['res.branch'].search([])
        for branch in branches:
            branch_target = self.env['branch.target'].create({
                'name' : self.name,
                'date_from':self.date_from,
                'date_to':self.date_to,
                'monthly_target_id':self.id,
                'branch_id':branch.id,
            })
            branch_target.update_branch_staff()
            
      


class BranchTarget(models.Model):
    _name = 'branch.target'
    _description = 'Branch Target'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(tracking=True)
    branch_id = fields.Many2one('res.branch',tracking=True)
    date_from = fields.Date(string='Date From',tracking=True)
    date_to = fields.Date(string='Date To',tracking=True)
    sale_target = fields.Float(string='Target',tracking=True)
    recovery_target = fields.Float(string='Recovery Target',tracking=True)

    sale_target_achieved = fields.Float('Sale Target Achieved',compute='compute_branch_sale')
    recovery_target_achieved = fields.Float('Recovery Target Achieved',compute='compute_branch_recovery')

    monthly_target_id = fields.Many2one('monthly.target',tracking=True)

    recover_officer_target_ids = fields.One2many('recovery.officer.target','branch_target_id')

    @api.onchange('recover_officer_target_ids','date_from','date_to','name')
    def update_recovery_line(self):
        for rec in self:
            for line in rec.recover_officer_target_ids:
                line.name = rec.name
                line.branch_id = rec.branch_id.id
                line.date_from = rec.date_from
                line.date_to = rec.date_to

    def compute_branch_sale(self):
        for rec in self:
            total = 0
            lease_sales = self.env['lease.sale'].search([('branch_id','=',rec.branch_id.id),
                                                         ('lease_date','>=',rec.date_from),
                                                         ('lease_date','<=',rec.date_to),
                                                         ('state','=','done')])
            for lease in lease_sales:
                total+=lease.sale_total
            rec.sale_target_achieved = total

    def compute_branch_recovery(self):
        for rec in self:
            total = 0
            recovery_payments = self.env['account.payment'].search([
                ('is_instalment','=',True),('payment_type','=','inbound'),('date','>=',rec.date_from),('date','<=',rec.date_to)
            ])
            branch_recovery = recovery_payments.filtered(lambda x:x.instalment_id.lease_sale_id.branch_id.id == rec.branch_id.id)
            for br in branch_recovery:
                total+=br.amount_total
            rec.recovery_target_achieved = total

    def update_branch_staff(self):
        branch_employees = self.env['hr.employee'].search([('branch_id','=',self.branch_id.id)])
        for employee in branch_employees:
            recover_officer_target = self.env['recovery.officer.target'].create({
                'name' : self.name,
                'date_from':self.date_from,
                'date_to':self.date_to,
                'branch_id':self.branch_id.id,
                'recovery_officer_id':employee.id
            })



class RecoveryOfficerTarget(models.Model):
    _name = 'recovery.officer.target'
    _description = 'Branch Recovery Officer Target'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(tracking=True)
    branch_id = fields.Many2one('res.branch',tracking=True)
    date_from = fields.Date(tracking=True)
    date_to = fields.Date(tracking=True)
    recovery_officer_id = fields.Many2one('hr.employee',tracking=True)
    job_position_id = fields.Many2one(related='recovery_officer_id.job_id')
    recovery_target = fields.Float(tracking=True)
    sale_target = fields.Float(tracking=True)
    target_achived = fields.Float(compute='compute_officer_recovery')
    branch_target_id = fields.Many2one('branch.target',tracking=True)

    def compute_officer_recovery(self):
        for rec in self:
            total = 0
            recovery_payments = self.env['account.payment'].search([
                ('is_instalment', '=', True), ('payment_type', '=', 'inbound'), ('date', '>=', rec.date_from),
                ('date', '<=', rec.date_to), ('recovery_officer_id','=',rec.recovery_officer_id.id)
            ])
            for br in recovery_payments:
                total += br.amount_total
            rec.target_achived = total


class ProductSaleIncentive(models.Model):
    _name = 'product.incentive'
    _description = 'Product Incentive'
    _rec_name = 'product_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    product_id = fields.Many2one('product.product',tracking=True)
    sale_type = fields.Selection([('cash','Cash Sale'),('lease','Lease Sale')],tracking=True)
    incentive_amount = fields.Float(string='Incentive Amount',tracking=True)




class SaleOrder(models.Model):
    _inherit = 'sale.order'


    saleman_id = fields.Many2one('hr.employee')

    def action_confirm(self):
        for line in self.order_line:
            line.update_product_incentive()
        res = super().action_confirm()
        return res

    def action_cancel(self):
        for line in self.order_line:
            line.unlink_sale_incentive_line()
        res = super().action_cancel()
        return res



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sale_incentive_id = fields.Many2one('sale.incentive')


    def update_product_incentive(self):
        if not self.sale_incentive_id:
            incentive_product = self.env['product.incentive'].search([('product_id','=',self.product_id.id),('sale_type','=','cash')])
            if incentive_product:
                commission_amount= incentive_product[0].incentive_amount * self.product_uom_qty
                sale_incentive_id = self.env['sale.incentive'].create({
                    'date' : fields.date.today(),
                    'salesman_id' : self.order_id.saleman_id.id,
                    'product_id' : self.product_id.id,
                    'product_qty' : self.product_uom_qty,
                    'commission_amount' : commission_amount,
                    'sale_type' : 'cash',
                    'sale_order_line_id' : self.id,
                })
                self.sale_incentive_id = sale_incentive_id.id
    def unlink_sale_incentive_line(self):
        if self.sale_incentive_id:
            self.sale_incentive_id.unlink()




class LeaseProductIncentive(models.Model):
    _name = 'sale.incentive'
    _description = 'Lease Product Sale Incentive line'
    _rec_name = 'salesman_id'


    date = fields.Date()
    salesman_id = fields.Many2one('hr.employee')
    product_id = fields.Many2one('product.product')
    product_qty = fields.Integer()
    commission_amount = fields.Float()
    sale_type = fields.Selection([('cash', 'Cash Sale'), ('lease', 'Lease Sale')])
    lease_sale_item_id = fields.Many2one('lease.sale.item')
    sale_order_line_id = fields.Many2one('sale.order.line')




class LeaseSale(models.Model):
    _inherit = 'lease.sale'


    def approve_state(self):
        for line in self.lease_sale_item_ids:
            line.update_product_incentive()
        res = super().approve_state()
        return res

class leaseSaleItem(models.Model):
    _inherit = 'lease.sale.item'

    sale_incentive_id = fields.Many2one('sale.incentive')


    def update_product_incentive(self):
        if not self.sale_incentive_id:
            incentive_product = self.env['product.incentive'].search([('product_id','=',self.product_id.id),('sale_type','=','lease')])
            if incentive_product:
                commission_amount= incentive_product[0].incentive_amount * self.qty
                sale_incentive_id = self.env['sale.incentive'].create({
                    'date' : fields.date.today(),
                    'salesman_id' : self.lease_sale_id.salesman_id.id,
                    'product_id' : self.product_id.id,
                    'product_qty' : self.qty,
                    'commission_amount' : commission_amount,
                    'sale_type' : 'lease',
                    'lease_sale_item_id' : self.id,
                })
                self.sale_incentive_id = sale_incentive_id.id



class LeaseIncentiveTable(models.Model):
    _name = 'lease.incentive.table'
    _rec_name = 'incentive_percentage'
    _description = 'Recovery Incentive Table'

    sequence = fields.Integer()
    reward = fields.Float()
    recovery_percentage = fields.Float()
    incentive_percentage = fields.Float()


class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    branch_id = fields.Many2one('res.branch')
