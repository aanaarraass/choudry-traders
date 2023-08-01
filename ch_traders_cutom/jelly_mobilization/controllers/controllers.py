# -*- coding: utf-8 -*-
# from odoo import http


# class JellyMobilization(http.Controller):
#     @http.route('/jelly_mobilization/jelly_mobilization', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jelly_mobilization/jelly_mobilization/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('jelly_mobilization.listing', {
#             'root': '/jelly_mobilization/jelly_mobilization',
#             'objects': http.request.env['jelly_mobilization.jelly_mobilization'].search([]),
#         })

#     @http.route('/jelly_mobilization/jelly_mobilization/objects/<model("jelly_mobilization.jelly_mobilization"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jelly_mobilization.object', {
#             'object': obj
#         })
