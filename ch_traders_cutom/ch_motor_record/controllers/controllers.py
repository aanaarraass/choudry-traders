# -*- coding: utf-8 -*-
# from odoo import http


# class ChMotorRecored(http.Controller):
#     @http.route('/ch_motor_recored/ch_motor_recored', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ch_motor_recored/ch_motor_recored/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ch_motor_recored.listing', {
#             'root': '/ch_motor_recored/ch_motor_recored',
#             'objects': http.request.env['ch_motor_recored.ch_motor_recored'].search([]),
#         })

#     @http.route('/ch_motor_recored/ch_motor_recored/objects/<model("ch_motor_recored.ch_motor_recored"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ch_motor_recored.object', {
#             'object': obj
#         })
