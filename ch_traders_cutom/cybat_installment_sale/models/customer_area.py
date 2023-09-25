from odoo import models, fields, api

class CustomerArea(models.Model):
    _name = 'customer.area'

    name = fields.Char()


class CustomerRoad(models.Model):
    _name = 'customer.road'

    name = fields.Char()

class CustomerCity(models.Model):
    _name = 'customer.city'

    name = fields.Char()