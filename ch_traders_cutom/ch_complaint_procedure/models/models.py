# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductComplaint(models.Model):
    _name = 'product.complaint'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Customer Product Complaint'


    active = fields.Boolean(default=True)

    name = fields.Char(string='Complaint No',copy=False, default=lambda self: _('New'),
        required=True, tracking=True, )
    date = fields.Date(tracking=True,default=fields.date.today())
    branch_id = fields.Many2one('res.branch', tracking=True)
    lease_id = fields.Many2one('lease.sale', tracking=True)
    ac = fields.Char(string='A/C',racking=True)
    Lease_date = fields.Date(string='Lease Date', tracking=True)
    partner_id = fields.Many2one('res.partner', tracking=True)
    area = fields.Char(tracking=True)
    road = fields.Char(tracking=True)
    address = fields.Char(tracking=True)
    recover_officer_id = fields.Many2one('res.users', tracking=True)
    product_ids = fields.Many2many('product.product')

    state = fields.Selection([('draft','Draft'),('in','In Process'),('done','Resolved')],default='draft')



    ph_no = fields.Char(string='PH#')
    fault = fields.Char(string='Fault')
    technician = fields.Char(string='Technician')
    t_address = fields.Text('Address')

    line_ids = fields.One2many('product.complaint.line','product_complaint_id')


    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('product.complaint') or _('New')
        res = super(ProductComplaint, self).create(vals)
        return res

    @api.onchange('lease_id')
    def auto_fill_form(self):
        for rec in self:
            rec.branch_id = rec.lease_id.branch_id.id
            rec.ac = rec.lease_id.account_no
            rec.Lease_date = rec.lease_id.lease_date
            rec.partner_id = rec.lease_id.partner_id.id
            # rec.area = rec.lease_id.partner_id.area
            # rec.road = rec.lease_id.partner_id.road
            rec.address = rec.lease_id.partner_id.contact_address
            rec.recover_officer_id = rec.lease_id.recovery_officer_id.id
            rec.product_ids = rec.lease_id.lease_sale_item_ids.product_id.mapped(lambda x:x.id)


    def complaint_in_process(self):
        self.state = 'in'

    def complaint_resolved(self):
        self.state = 'done'

    def reopen_complaint(self):
        self.state = 'in'





class ProductComplaintLines(models.Model):
    _name = 'product.complaint.line'


    technician_visit_date = fields.Date('Technician Visit Date')
    remarks = fields.Char(string="Remarks")
    parts = fields.Char(string='Parts')
    status = fields.Selection([('yes','Yes'),('no','No')],string='YES/NO')

    product_complaint_id = fields.Many2one('product.complaint')
