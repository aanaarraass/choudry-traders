# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.models import BaseModel
from collections import defaultdict, OrderedDict

from odoo import SUPERUSER_ID
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError


from datetime import datetime, timedelta
from odoo import models, api




class PricelistItemHistory(models.Model):
    _name = "product.pricelist.item.history"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product Item History'


    name = fields.Char()


class PricelistItem(models.Model):
    _name = 'product.pricelist.item'
    _inherit = ['product.pricelist.item','mail.thread', 'mail.activity.mixin']



    def write(self, vals):
        name = ''
        for key, value in vals.items():
            name += str(key)+'-->'+str(value)+'/n'
        history = self.env['product.pricelist.item.history'].create({
            'name': name
        })
        res= super().write(vals)
        return res

    product_tmpl_id = fields.Many2one(
        'product.template', 'Product', ondelete='cascade',tracking=True, check_company=True,
        help="Specify a template if this rule only applies to one product template. Keep empty otherwise.")
    product_id = fields.Many2one(
        'product.product', 'Product Variant',tracking=True, ondelete='cascade', check_company=True,
        help="Specify a product if this rule only applies to one product. Keep empty otherwise.")

    min_quantity = fields.Float(
        'Min. Quantity',tracking=True, default=0, digits="Product Unit Of Measure",
        help="For the rule to apply, bought/sold quantity must be greater "
             "than or equal to the minimum quantity specified in this field.\n"
             "Expressed in the default unit of measure of the product.")

    date_start = fields.Datetime('Start Date',tracking=True, help="Starting datetime for the pricelist item validation\n"
                                                    "The displayed value depends on the timezone set in your preferences.")
    date_end = fields.Datetime('End Date',tracking=True, help="Ending datetime for the pricelist item validation\n"
                                                "The displayed value depends on the timezone set in your preferences.")

    fixed_price = fields.Float('Fixed Price',tracking=True, digits='Product Price')
