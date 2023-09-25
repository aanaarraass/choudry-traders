from odoo import models, fields, api

class ResBranch(models.Model):
    _inherit = 'res.branch'


    branch_code = fields.Char(string='Brnach Code',size=3)