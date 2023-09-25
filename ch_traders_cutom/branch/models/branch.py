from odoo import api, fields, models, _


class ResBranch(models.Model):
    _name = 'res.branch'
    _description = 'Branch'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True,tracking=True)
    company_id = fields.Many2one('res.company', required=True,tracking=True)
    telephone = fields.Char(string='Telephone No',tracking=True)
    address = fields.Text('Address',tracking=True)

    branch_manager_id = fields.Many2one('res.users')