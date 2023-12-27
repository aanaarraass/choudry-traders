from odoo import models, fields, api


class Area(models.Model):
    _name = 'area.area'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Business Area'

    name = fields.Char(string='Area Name',tracking=True)
    branch_id = fields.Many2one('res.branch',tracking=True)
    area_supervisor_id = fields.Many2one('hr.employee',tracking=True)
    


class ResBranch(models.Model):
    _inherit = 'res.branch'

    area_ids = fields.One2many('area.area','branch_id')

