# -*- coding: utf-8 -*-
# from odoo import http


# class AcesPayroll(http.Controller):
#     @http.route('/cyb_payroll/cyb_payroll/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cyb_payroll/cyb_payroll/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cyb_payroll.listing', {
#             'root': '/cyb_payroll/cyb_payroll',
#             'objects': http.request.env['cyb_payroll.cyb_payroll'].search([]),
#         })

#     @http.route('/cyb_payroll/cyb_payroll/objects/<model("cyb_payroll.cyb_payroll"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cyb_payroll.object', {
#             'object': obj
#         })
