from odoo import models, fields, api,_


class Guarantor(models.Model):
    _name = 'guarantor'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Guarantor'

    name = fields.Char('Name',tracking=True,)
    image_1920 = fields.Image()
    comment = fields.Char('Note',tracking=True,)
    function = fields.Char('Designation',tracking=True,)
    contact_address = fields.Char('Currant Address',tracking=True,)
    state = fields.Selection([('draft', 'Draft'), ('select', 'Select'), ('reject', 'Reject')],default='draft',tracking=True,)
    registration_no = fields.Char(
        'Registration ID', copy=False, default=lambda self: _('New'),
        required=True,tracking=True,)
    reg_date = fields.Date(default=fields.date.today(), string='Registration Date',tracking=True,)
    reg_status = fields.Selection([('new', 'New'), ('old', 'Old')], string='Status',tracking=True,)

    recovery_officer_id = fields.Many2one('res.users',tracking=True,)
    salesman_id = fields.Many2one('res.users',tracking=True,)
    approved_by_id = fields.Many2one('res.users',tracking=True,)
    nick_name = fields.Char('Nick Name',tracking=True,)
    cnic = fields.Integer('CNIC',tracking=True,)
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

    customer_id = fields.Many2one('res.partner',tracking=True,)

    _sql_constraints = [
        ('cnic_uniq', 'unique (cnic)',
         'Guarantor Registration Already Exists !'),
    ]

    @api.model
    def create(self, vals):
        vals['reg_date'] = fields.date.today()
        if vals.get('registration_no', _('New')) == _('New'):
            vals['registration_no'] = self.env['ir.sequence'].next_by_code('guarantor.seq') or _('New')
        return super(Guarantor, self).create(vals)


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