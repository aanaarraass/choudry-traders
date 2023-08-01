from odoo import models, fields, api


class Area(models.Model):
    _name = 'area.area'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(track_visibility= "Always")
    branch_id = fields.Many2one('res.branch')

