from datetime import timedelta

from odoo import models, fields, api


class PurchaseOrderWizard(models.TransientModel):
    """ Wizard allowing to grant a badge to a user"""
    _name = 'purchase.order.wizard'
    _description = 'PurchaseOrderWizard'

    partner_id = fields.Many2one(comodel_name='res.partner', string='Vendor')
    wizard_product_line = fields.One2many(comodel_name='purchase.order.wizard.line', inverse_name='wizard_id')

    def action_confirm(self):
        active_id = self._context.get('active_id')
        purchase_order = self.env['purchase.order'].browse(active_id)
        print('active id =======>', purchase_order)
        o2m_list = []
        for rec in self:
            for line in rec.wizard_product_line:
                if line.qty_tobuy > 0:
                    o2m_list.append((0, 0, {
                        'product_id': line.product_id.id,
                        'product_qty': line.qty_tobuy,
                        'price_unit': line.price_unit,
                    }))
            purchase_order.update({
                'partner_id': rec.partner_id.id,
                'order_line': o2m_list
            })

    @api.onchange('partner_id')
    def get_all_products(self):
        self.wizard_product_line = False
        for rec in self:
            products = self.env['product.product'].search([]).filtered(lambda lm: lm.seller_ids.name in self.partner_id)
            rec.write({
                'wizard_product_line': [(0, 0, {'product_id': product.id}) for product in products]
            })

    # @api.model
    # def default_get(self, fields):
    #     res = super(PurchaseOrderWizard, self).default_get(fields)
    #     value = self.env['purchase.order'].browse(int(self._context.get('active_id')))
    #     if value:
    #         self.partner_id = value.partner_id.id
    #     return res


class PurchaseOrderWizardLine(models.TransientModel):
    """ Wizard allowing to grant a badge to a user"""
    _name = 'purchase.order.wizard.line'

    product_id = fields.Many2one(comodel_name='product.product', string='Product Name')
    wizard_id = fields.Many2one(comodel_name='purchase.order.wizard', ondelete='cascade')
    qty_available = fields.Float('Available Qty', compute='_compute_sold_qty')
    qty_sold = fields.Float('Sold Qty', compute='_compute_sold_qty')
    last_week_sale = fields.Float("7 day Sale", compute='_compute_last_week_sale')
    last_purchase_price = fields.Float('Last Price')
    qty_tobuy = fields.Float('Qty to Buy')
    price_unit = fields.Float('New Price')

    @api.depends('product_id')
    def _compute_sold_qty(self):
        for rec in self:
            if rec.product_id:
                products = self.env['product.product'].search([('id', '=', rec.product_id.id)])
                for product in products:
                    rec.qty_available = product.qty_available
                    rec.qty_sold = product.sales_count
                    rec.last_purchase_price = product.last_purchase_price
            else:
                rec.qty_available = 0.0
                rec.qty_sold = 0.0
                rec.last_purchase_price = 0.0

    @api.depends('qty_sold')
    def _compute_last_week_sale(self):
        start_date = fields.Date.today()
        end_date = start_date + timedelta(days=-7)
        sales = self.env['sale.order'].search(
            [('state', 'in', ('sale', 'done')), ('date_order', '<=', start_date), ('date_order', '>=', end_date)])
        for rec in self:
            week_qty = 0
            for s in sales:
                orders = self.env['sale.order.line'].search([
                    ('order_id', '=', s.id), ('product_id', '=', rec.product_id.id)
                ])
                week_qty += sum(orders.mapped('product_uom_qty'))

            rec.last_week_sale = week_qty


