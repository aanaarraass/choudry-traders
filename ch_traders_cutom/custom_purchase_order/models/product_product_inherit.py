from odoo import models, fields, api


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    last_purchase_price = fields.Float('Last Purchase Price')


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    last_purchase_price = fields.Float('Last Purchase Price')

