# -*- coding: utf-8 -*-
# from odoo import http


# class ChComplaintProcedure(http.Controller):
#     @http.route('/ch_complaint_procedure/ch_complaint_procedure', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ch_complaint_procedure/ch_complaint_procedure/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ch_complaint_procedure.listing', {
#             'root': '/ch_complaint_procedure/ch_complaint_procedure',
#             'objects': http.request.env['ch_complaint_procedure.ch_complaint_procedure'].search([]),
#         })

#     @http.route('/ch_complaint_procedure/ch_complaint_procedure/objects/<model("ch_complaint_procedure.ch_complaint_procedure"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ch_complaint_procedure.object', {
#             'object': obj
#         })
