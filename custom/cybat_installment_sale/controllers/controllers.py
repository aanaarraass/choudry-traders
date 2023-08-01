# -*- coding: utf-8 -*-
# from odoo import http


# class CybatInstallmentSale(http.Controller):
#     @http.route('/cybat_installment_sale/cybat_installment_sale', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cybat_installment_sale/cybat_installment_sale/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cybat_installment_sale.listing', {
#             'root': '/cybat_installment_sale/cybat_installment_sale',
#             'objects': http.request.env['cybat_installment_sale.cybat_installment_sale'].search([]),
#         })

#     @http.route('/cybat_installment_sale/cybat_installment_sale/objects/<model("cybat_installment_sale.cybat_installment_sale"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cybat_installment_sale.object', {
#             'object': obj
#         })
