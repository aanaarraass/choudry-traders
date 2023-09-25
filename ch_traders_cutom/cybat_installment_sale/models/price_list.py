# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Pricelist(models.Model):
    _inherit= "product.pricelist"


    is_instalment_price_list = fields.Boolean(string='Installment Price List')