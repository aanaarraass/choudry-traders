# -*- coding: utf-8 -*-
# from odoo import http


# class LeaseReporting(http.Controller):
#     @http.route('/lease_reporting/lease_reporting', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lease_reporting/lease_reporting/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('lease_reporting.listing', {
#             'root': '/lease_reporting/lease_reporting',
#             'objects': http.request.env['lease_reporting.lease_reporting'].search([]),
#         })

#     @http.route('/lease_reporting/lease_reporting/objects/<model("lease_reporting.lease_reporting"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lease_reporting.object', {
#             'object': obj
#         })
