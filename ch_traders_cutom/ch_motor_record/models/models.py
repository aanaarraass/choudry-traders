# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MotorbikeRecored(models.Model):
    _name = 'motorbike.record'
    _description = 'Motorbike Record'
    _rec_name = 'chasis_number'
    _inherit = ['mail.thread', 'mail.activity.mixin', ]

    state = fields.Selection([('draft', 'Draft'), ('received', 'Received'), ('delivered','Delivered')],default='draft')
    sale_type = fields.Selection([('cash', 'Cash'), ('lease', 'Lease')])

    date = fields.Date()
    branch_id = fields.Many2one('res.branch')
    product_id = fields.Many2one('product.product')
    vendor_id = fields.Many2one('res.partner')
    engine_number = fields.Char()
    chasis_number = fields.Char()
    letter_received_date = fields.Date()
    letter_status = fields.Selection([('name', 'By Name'), ('open', 'Open')])
    letter_name = fields.Char()

    # for lease
    account_no = fields.Char()
    lease_id = fields.Many2one('lease.sale')
    customer_id = fields.Many2one('res.partner')
    father_name = fields.Char()
    address = fields.Char()
    area_id = fields.Many2one('customer.area')
    phone_number = fields.Char()
    cnic_no = fields.Char()

    # for cash
    invoice_id = fields.Many2one('account.move')

    # vehical information

    model_name = fields.Char()
    colour = fields.Char()
    vehicle_name = fields.Char()

    # registration

    agent_id = fields.Many2one('res.partner',tracking=True)
    registration_date = fields.Date(tracking=True)
    registration_no = fields.Char(tracking=True)
    registration_person = fields.Char(tracking=True)
    registration_person_cnic = fields.Char(tracking=True)
    registration_phone = fields.Char(tracking=True)

    registration_slip_received_date = fields.Date(tracking=True)
    number_plate_received_date = fields.Date(tracking=True)
    smart_card_received_date = fields.Date(tracking=True)
    file_received_date = fields.Date(tracking=True)

    number_plate_delivered_to = fields.Char(tracking=True)
    number_plate_delivered_date = fields.Date(tracking=True)
    smart_card_delivered_to = fields.Char(tracking=True)
    smart_card_delivered_date = fields.Date(tracking=True)
    file_delivered_to = fields.Char(tracking=True)
    file_delivered_date = fields.Date(tracking=True)
    delivered_by = fields.Char(tracking=True)
    delivered_by_date = fields.Date(tracking=True)


    def document_received(self):
        self.state = 'received'


    def document_delivered(self):
        self.state = 'delivered'

    def reset_draft(self):
        self.state = 'draft'

    @api.onchange('lease_id')
    def auto_fetch_information(self):
        for rec in self:
            rec.customer_id = rec.lease_id.partner_id.id
            rec.branch_id = rec.lease_id.branch_id.id
            rec.father_name = rec.lease_id.partner_id.parent_name
            rec.address = rec.lease_id.partner_id.contact_address
            rec.area_id = rec.lease_id.partner_id.customer_address_area_id.id
            rec.phone_number = rec.lease_id.partner_id.phone_number
            rec.cnic_no = rec.lease_id.partner_id.cnic


    @api.onchange('invoice_id')
    def auto_fetch_information_invoice(self):
        for rec in self:
            rec.customer_id = rec.invoice_id.partner_id.id
            rec.branch_id = rec.invoice_id.branch_id.id
            rec.father_name = rec.invoice_id.partner_id.parent_name
            rec.address = rec.invoice_id.partner_id.contact_address
            rec.area_id = rec.invoice_id.partner_id.customer_address_area_id.id
            rec.phone_number = rec.invoice_id.partner_id.phone_number
            rec.cnic_no = rec.invoice_id.partner_id.cnic
