# -*- coding: utf-8 -*-
# from odoo import http


# class ChPriceList(http.Controller):
#     @http.route('/ch_price_list/ch_price_list', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ch_price_list/ch_price_list/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ch_price_list.listing', {
#             'root': '/ch_price_list/ch_price_list',
#             'objects': http.request.env['ch_price_list.ch_price_list'].search([]),
#         })

#     @http.route('/ch_price_list/ch_price_list/objects/<model("ch_price_list.ch_price_list"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ch_price_list.object', {
#             'object': obj
#         })
