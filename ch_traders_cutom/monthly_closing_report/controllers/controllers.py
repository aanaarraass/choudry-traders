# -*- coding: utf-8 -*-
# from odoo import http


# class MonthlyClosingReport(http.Controller):
#     @http.route('/monthly_closing_report/monthly_closing_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/monthly_closing_report/monthly_closing_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('monthly_closing_report.listing', {
#             'root': '/monthly_closing_report/monthly_closing_report',
#             'objects': http.request.env['monthly_closing_report.monthly_closing_report'].search([]),
#         })

#     @http.route('/monthly_closing_report/monthly_closing_report/objects/<model("monthly_closing_report.monthly_closing_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('monthly_closing_report.object', {
#             'object': obj
#         })
