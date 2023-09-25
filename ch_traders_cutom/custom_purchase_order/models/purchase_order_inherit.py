from odoo import models, fields, api
from datetime import datetime, timedelta

from odoo.tools import float_compare


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    # def action_get_history_product(self):
    #     for line in self.order_line:
    #         print('line=================>', line, line.product_id.id, line.product_id.name, line.product_id.last_purchase_price,
    #               [x.name for x in line.product_id.product_template_variant_value_ids])
    #         products = self.env['product.product'].search([('id', '=', line.product_id.id)])
    #         print('products=================>', products, products.name, products.last_purchase_price)
    #         if products:
    #             if float_compare(products.last_purchase_price, line.price_unit, 2) != 0:
    #                 products.write({
    #                     'last_purchase_price': line.price_unit
    #                 })

    @api.model
    def create(self, vals):
        print('create=====================', self)
        res = super(PurchaseOrderInherit, self).create(vals)
        for line in res.order_line:
            print('line=================>', line, line.product_id.id, line.product_id.name,
                  line.product_id.last_purchase_price,
                  [x.name for x in line.product_id.product_template_variant_value_ids])
            products = self.env['product.product'].search([('id', '=', line.product_id.id)])
            print('products=================>', products, products.name, products.last_purchase_price)
            if products:
                if float_compare(products.last_purchase_price, line.price_unit, 2) != 0:
                    products.write({
                        'last_purchase_price': line.price_unit
                    })
        return res

    # def write(self, vals):
    #     res = super(PurchaseOrderInherit, self).write(vals)
    #     for line in self.order_line:
    #         print('line=================>', line, line.product_id.id, line.product_id.name,
    #               line.product_id.last_purchase_price,
    #               [x.name for x in line.product_id.product_template_variant_value_ids])
    #         products = self.env['product.product'].search([('id', '=', line.product_id.id)])
    #         print('products=================>', products, products.name, products.last_purchase_price)
    #         if products:
    #             if float_compare(products.last_purchase_price, line.price_unit, 2) != 0:
    #                 products.write({
    #                     'last_purchase_price': line.price_unit
    #                 })
    #     return res


