from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Cast(models.Model):
    _name = 'cast.cast'

    name = fields.Char()


class MaritalStatus(models.Model):
    _name = 'marital.status'

    name = fields.Char()


class ResidentialStatus(models.Model):
    _name = 'residential.status'

    name = fields.Char()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_lease_customer = fields.Boolean()
    state = fields.Selection([('draft', 'Draft'), ('select', 'Select'), ('reject', 'Reject')], default='draft',
                             string='Status',tracking=True,)
    registration_no = fields.Char(
        'Registration ID', copy=False, default=lambda self: _('New'),
        required=True,tracking=True,)
    reg_date = fields.Date(default=fields.date.today(), string='Registration Date',tracking=True,)
    reg_status = fields.Selection([('new', 'New'), ('old', 'Old')], string='Status',tracking=True,)

    recovery_officer_id = fields.Many2one('res.users',tracking=True,)
    salesman_id = fields.Many2one('res.users',tracking=True,)
    approved_by_id = fields.Many2one('res.users',tracking=True,)
    nick_name = fields.Char('Nick Name',tracking=True,)
    cnic = fields.Char('CNIC',tracking=True,)
    son_off = fields.Char(string='S/O,W/O,D/O',tracking=True,)
    cast_id = fields.Many2one('cast.cast', string='Cast',tracking=True,)
    age = fields.Integer(string='Age',tracking=True,)
    marital_status_id = fields.Many2one('marital.status', string='Marital Status',tracking=True,)
    home_since = fields.Date('Living At Home Since',tracking=True,)
    address_status = fields.Many2one('residential.status',tracking=True,)
    area_since = fields.Date('Living At Area Since',tracking=True,)
    near_by = fields.Char('Near By',tracking=True,)
    area = fields.Char('Area',tracking=True,)
    road = fields.Char('Road',tracking=True,)
    city = fields.Char(tracking=True,)
    parmanent_address = fields.Char('Permanent Address',tracking=True,)
    phone_number = fields.Char('Phone',tracking=True,)
    relation_id = fields.Many2one('relation',tracking=True,)

    emp_type = fields.Selection([('self', 'Self Employed'), ('Salary', 'Salary Person')], string='Employment Type',tracking=True,)
    business_type = fields.Char('Business/Company Type',tracking=True,)
    working_since = fields.Date(string='Working Since',tracking=True,)
    income = fields.Float('Salary/Income',tracking=True,)
    office_phone = fields.Char('Phone Number',tracking=True,)
    business_address = fields.Text('Business Address',tracking=True,)
    guarantor_ids = fields.Many2many('guarantor',tracking=True,)

    advance_paymeny_id = fields.Many2one('account.move',tracking=True,)
    advance_amount = fields.Monetary(related='advance_paymeny_id.amount_total_signed',tracking=True,)

    ref_person = fields.Char('Reference Person',tracking=True,)
    ref_relation_id = fields.Many2one('relation', string='Relation',tracking=True,)
    lease_count = fields.Integer(compute='lease_sale_count',tracking=True,)

    is_decesced = fields.Boolean('Deceased Customer',tracking=True,)
    is_defaulter = fields.Boolean('Defaulter Customer',tracking=True,)


    _sql_constraints = [
        ('cnic_uniq', 'unique (cnic)',
         'Customer Registration Already Exists !'),
    ]

    def lease_sale_count(self):
        self.lease_count = self.env['lease.sale'].search_count([('partner_id', '=', self.id)])

    def mark_deceased_customer(self):
        self.is_decesced = True

    def mark_defaulter_customer(self):
        self.is_defaulter = True

    def view_advance_payment(self):
        self.ensure_one()
        return {
            'name': _('Advance Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', '=', self.advance_paymeny_id.id)],
        }

    @api.model
    def create(self, vals):
        # if vals['is_lease_customer'] == True:
        vals['reg_date'] = fields.date.today()
        if vals.get('registration_no', _('New')) == _('New'):
            vals['registration_no'] = self.env['ir.sequence'].next_by_code('lease.customer') or _('New')
        return super(ResPartner, self).create(vals)

    def approved(self):
        self.state = 'select'
        self.approved_by_id = self.env.user.id

    def reject(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Reason'),
            'view_mode': 'form',
            'res_model': 'reject.reason',
            'target': 'new',
            'res_id': False,
        }

    def reset_draft(self):
        self.state = 'draft'

    def advance_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Advance Payment'),
            'view_mode': 'form',
            'res_model': 'lease.sale.advance.payment',
            'target': 'new',
            'res_id': False,
        }

    def create_lease_sale(self):
        # check customer status
        if self.state != 'select':
            raise ValidationError('Customer Status Not Approved yet!')
        # guarantor status check
        # for guarantor in self.guarantor_ids:
        #     if guarantor.state != 'select':
        #         raise ValidationError('Guarantor Status Not Approved!')
        done_gurantor=len(self.guarantor_ids.filtered(lambda x: x.state == 'select'))
        if done_gurantor < 2:
            raise ValidationError('Two Guarantor Status must be Select!')

        lease_sale = self.env['lease.sale'].create({
            'partner_id': self.id,
            'ref_person': self.ref_person,
            'ref_relation_id': self.ref_relation_id.id,
            'guarantor_ids': self.guarantor_ids.ids,
            'state': 'draft',
            'advance_payment_ids':self.advance_paymeny_id,
        })
        self.advance_paymeny_id = False
        return {
            'name': _('Lease Sale'),
            'type': 'ir.actions.act_window',
            'res_model': 'lease.sale',
            'view_mode': 'form',
            'res_id':lease_sale.id,
        }

    def view_lease_sale(self):
        return {
            'name': _('Lease Sale'),
            'type': 'ir.actions.act_window',
            'res_model': 'lease.sale',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
        }
