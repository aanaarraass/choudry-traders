from odoo import models, fields, api

class Users(models.Model):
    _inherit = 'res.users'


    supervisor_id = fields.Many2one('res.users')
    branch_manager_id = fields.Many2one('res.users')