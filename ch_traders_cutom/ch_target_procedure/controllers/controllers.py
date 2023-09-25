# -*- coding: utf-8 -*-
# from odoo import http


# class ChTargetProcedure(http.Controller):
#     @http.route('/ch_target_procedure/ch_target_procedure', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ch_target_procedure/ch_target_procedure/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ch_target_procedure.listing', {
#             'root': '/ch_target_procedure/ch_target_procedure',
#             'objects': http.request.env['ch_target_procedure.ch_target_procedure'].search([]),
#         })

#     @http.route('/ch_target_procedure/ch_target_procedure/objects/<model("ch_target_procedure.ch_target_procedure"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ch_target_procedure.object', {
#             'object': obj
#         })
