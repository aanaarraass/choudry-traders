from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    pricelist_type = fields.Selection([('market', 'Market Rate'), ('whole', 'Wholesale'),
                                       ('retail', 'Retail'), ('p1', 'Package 1'), ('p2', 'Package 2'),
                                       ('p3', 'Package 3'), ('p4', 'Package 4')])

    no_of_installment = fields.Integer(string='Number Of Installment')


class UpdatePricelist(models.Model):
    _name = 'update.pricelist'
    _description = 'Pricelist Update'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='SR#', track_visibility="Always",copy=False,
                        default=lambda self: _('New'),required=True)
    state = fields.Selection([('draft','Draft'),('done','Done')],default='draft',copy=False)
    date = fields.Date(default=fields.date.today())

    update_price = fields.Selection([('all', 'All'), ('brand', 'Brand Wise')],default='all',required=1)

    brand_id = fields.Many2one('product.brand')

    wholesale_percentage = fields.Float()
    retail_percentage = fields.Float()

    custome_pricelist_ids = fields.One2many('custom.pricelist', 'update_pricelist_id')


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('pricelist.serial') or _('New')
        return super(UpdatePricelist, self).create(vals)
    def get_products(self):
        previous_lines = self.custome_pricelist_ids
        if previous_lines:
            for previou_line in previous_lines:
                previou_line.unlink()

        if self.update_price == 'all':
            products = self.env['product.product'].search([('detailed_type','=','product')])
            for product in products:
                line = self.env['custom.pricelist'].create({
                    'item': product.id,
                    'purchase_rate': product.standard_price,
                    'whole_sale_percentage': self.wholesale_percentage,
                    'whole_sale_rate': round(
                        (product.standard_price * self.wholesale_percentage) / 100 + product.standard_price, 0),
                    'retail_sale': round(
                        (product.standard_price * self.retail_percentage) / 100 + product.standard_price, 0),
                    'retail_sale_percentage': self.retail_percentage,
                    'update_pricelist_id': self.id
                })
        elif self.update_price == 'brand':
            products = self.env['product.product'].search([('brand_id', '=', self.brand_id.id)])
            for product in products:
                line = self.env['custom.pricelist'].create({
                    'item': product.id,
                    'purchase_rate': product.standard_price,
                    'whole_sale_percentage': self.wholesale_percentage,
                    'whole_sale_rate': round((product.standard_price * self.wholesale_percentage)/100 + product.standard_price,0),
                    'retail_sale': round((product.standard_price * self.retail_percentage)/100 + product.standard_price,0),
                    'retail_sale_percentage': self.retail_percentage,
                    'update_pricelist_id': self.id
                })

    def update_prices_in_pricelist(self):
        for line in self.custome_pricelist_ids:
            pricelists = self.env['product.pricelist'].search([])
            market_pricelist = pricelists.filtered(lambda x:x.pricelist_type == 'market')
            wholesale_pricelist = pricelists.filtered(lambda x:x.pricelist_type == 'whole')
            retail_pricelist = pricelists.filtered(lambda x:x.pricelist_type == 'retail')
            p1_pricelist = pricelists.filtered(lambda x:x.pricelist_type == 'p1')
            p2_pricelist = pricelists.filtered(lambda x:x.pricelist_type == 'p2')
            p3_pricelist = pricelists.filtered(lambda x:x.pricelist_type == 'p3')
            p4_pricelist = pricelists.filtered(lambda x:x.pricelist_type == 'p4')
            product_in_market_pricelist = market_pricelist.item_ids.filtered(lambda y:y.product_id.id ==  line.item.id)
            product_in_wholesale_pricelist = wholesale_pricelist.item_ids.filtered(lambda y:y.product_id.id ==  line.item.id)
            product_in_retail_pricelist = retail_pricelist.item_ids.filtered(lambda y:y.product_id.id ==  line.item.id)
            package_1_pricelist = p1_pricelist.item_ids.filtered(lambda y:y.product_id.id ==  line.item.id)
            package_2_pricelist = p2_pricelist.item_ids.filtered(lambda y:y.product_id.id ==  line.item.id)
            package_3_pricelist = p3_pricelist.item_ids.filtered(lambda y:y.product_id.id ==  line.item.id)
            package_4_pricelist = p4_pricelist.item_ids.filtered(lambda y:y.product_id.id ==  line.item.id)
            if product_in_market_pricelist:
                if line.purchase_rate < line.market_rate:
                    product_in_market_pricelist.fixed_price = line.market_rate
                else:
                    if self.env.user.has_group('cybat_pricelist_ch.update_pricelist_admin'):
                        product_in_market_pricelist.fixed_price = line.market_rate
                    else:
                        raise ValidationError(_('You Are Not Allowed to update market price less than Purchase Price.'))
            else:
                pricelist_item = self.env['product.pricelist.item'].create({
                    'product_tmpl_id':line.item.product_tmpl_id.id,
                    'product_id' : line.item.id,
                    'pricelist_id':market_pricelist.id,
                    'fixed_price':line.market_rate,
                    'min_quantity':1.00
                })
            if product_in_wholesale_pricelist:
                product_in_wholesale_pricelist.fixed_price = line.whole_sale_rate
            else:
                pricelist_item = self.env['product.pricelist.item'].create({
                    'product_tmpl_id': line.item.product_tmpl_id.id,
                    'product_id': line.item.id,
                    'pricelist_id': wholesale_pricelist.id,
                    'fixed_price': line.whole_sale_rate,
                    'min_quantity': 1.00
                })
            if product_in_retail_pricelist:
                product_in_retail_pricelist.fixed_price = line.retail_sale
            else:
                pricelist_item = self.env['product.pricelist.item'].create({
                    'product_tmpl_id': line.item.product_tmpl_id.id,
                    'product_id': line.item.id,
                    'pricelist_id': retail_pricelist.id,
                    'fixed_price': line.retail_sale,
                    'min_quantity': 1.00
                })
            if package_1_pricelist:
                package_1_pricelist.fixed_price = line.package_1
            else:
                pricelist_item = self.env['product.pricelist.item'].create({
                    'product_tmpl_id': line.item.product_tmpl_id.id,
                    'product_id': line.item.id,
                    'pricelist_id': p1_pricelist.id,
                    'fixed_price': line.package_1,
                    'min_quantity': 1.00
                })
            if package_2_pricelist:
                package_2_pricelist.fixed_price = line.package_2
            else:
                pricelist_item = self.env['product.pricelist.item'].create({
                    'product_tmpl_id': line.item.product_tmpl_id.id,
                    'product_id': line.item.id,
                    'pricelist_id': p2_pricelist.id,
                    'fixed_price': line.package_2,
                    'min_quantity': 1.00
                })
            if package_3_pricelist:
                package_3_pricelist.fixed_price = line.package_3
            else:
                pricelist_item = self.env['product.pricelist.item'].create({
                    'product_tmpl_id': line.item.product_tmpl_id.id,
                    'product_id': line.item.id,
                    'pricelist_id': p3_pricelist.id,
                    'fixed_price': line.package_3,
                    'min_quantity': 1.00
                })
            if package_4_pricelist:
                package_4_pricelist.fixed_price = line.package_4
            else:
                pricelist_item = self.env['product.pricelist.item'].create({
                    'product_tmpl_id': line.item.product_tmpl_id.id,
                    'product_id': line.item.id,
                    'pricelist_id': p4_pricelist.id,
                    'fixed_price': line.package_4,
                    'min_quantity': 1.00
                })
            self.state = 'done'
        self.generate_user_mesasge()

    def generate_user_mesasge(self):
        users = self.env['res.users'].search([('share','=',False)])
        for user in users:
            activity = self.env['mail.activity'].sudo().create({
                'activity_type_id': 4,
                'date_deadline': fields.date.today(),
                'summary': 'Pricelist New update Please Check',
                'user_id': user.id,
                'res_id': self.id,
                'res_model_id': self.env['ir.model'].search([('model', '=', 'update.pricelist')], limit=1).id,
            })


class CustomPrice(models.Model):
    _name = "custom.pricelist"
    _description = "Custom pricelist"

    item = fields.Many2one('product.product', string="Item")
    purchase_rate = fields.Float(string="Purchase Rate")
    market_rate = fields.Float(string="Market_Rate")
    whole_sale_rate = fields.Float(string="Whole_Sale_Rate")
    whole_sale_percentage = fields.Float(string="Whole_Sale_Percentage")
    retail_sale_percentage = fields.Float(string="Retail_Sale_Percentage")
    retail_sale = fields.Float(string="Retail Sale")
    package_1 = fields.Float(string="Package 1")
    package_2 = fields.Float(string="Package 2")
    package_3 = fields.Float(string="Package 3")
    package_4 = fields.Float(string="Package 4")

    update_pricelist_id = fields.Many2one('update.pricelist')

    @api.onchange('whole_sale_percentage')
    def update_wholesale_rate(self):
        self.whole_sale_rate = (self.item.standard_price * self.whole_sale_percentage)/100 + self.item.standard_price

    @api.onchange('retail_sale_percentage')
    def update_retail_rate(self):
        self.retail_sale = (self.item.standard_price * self.retail_sale_percentage) / 100 + self.item.standard_price
