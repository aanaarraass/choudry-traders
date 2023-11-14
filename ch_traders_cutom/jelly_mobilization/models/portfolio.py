from odoo import models, fields, api


class Area(models.Model):
    _name = 'branch.portfolio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Portfolio '

    name = fields.Char(track_visibility= "Always")
    area_id = fields.Many2many('area.area')
    recovery_id = fields.Many2one('hr.employee',string='Recovery Officer')
