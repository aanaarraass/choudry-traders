# -*- coding: utf-8 -*-
# from odoo import http


# class OmRecoveryReporting(http.Controller):
#     @http.route('/om_recovery_reporting/om_recovery_reporting', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/om_recovery_reporting/om_recovery_reporting/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('om_recovery_reporting.listing', {
#             'root': '/om_recovery_reporting/om_recovery_reporting',
#             'objects': http.request.env['om_recovery_reporting.om_recovery_reporting'].search([]),
#         })

#     @http.route('/om_recovery_reporting/om_recovery_reporting/objects/<model("om_recovery_reporting.om_recovery_reporting"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('om_recovery_reporting.object', {
#             'object': obj
#         })
