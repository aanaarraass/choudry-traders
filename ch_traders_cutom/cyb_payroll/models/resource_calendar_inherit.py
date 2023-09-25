# -*- coding: utf-8 -*-

from odoo import models, fields, api
import pytz


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'
    _description = 'ResourceCalendar'


    grace_time = fields.Float('Graced Time')

