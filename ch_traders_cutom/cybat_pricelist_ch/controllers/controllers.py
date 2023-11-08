# -*- coding: utf-8 -*-
# from odoo import http


# class CybatPricelistCh(http.Controller):
#     @http.route('/cybat_pricelist_ch/cybat_pricelist_ch', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cybat_pricelist_ch/cybat_pricelist_ch/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cybat_pricelist_ch.listing', {
#             'root': '/cybat_pricelist_ch/cybat_pricelist_ch',
#             'objects': http.request.env['cybat_pricelist_ch.cybat_pricelist_ch'].search([]),
#         })

#     @http.route('/cybat_pricelist_ch/cybat_pricelist_ch/objects/<model("cybat_pricelist_ch.cybat_pricelist_ch"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cybat_pricelist_ch.object', {
#             'object': obj
#         })
