from odoo import models, fields, api


class Area(models.Model):
    _name = 'branch.portfolio'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(track_visibility= "Always")
    branch_id = fields.Many2one('res.branch')
    area_ids = fields.Many2many('area.area')
    recovery_id = fields.Many2one('res.users',string='Recovery Officer')
    branch_manager_id = fields.Many2one('res.users',string='Branch Manager')