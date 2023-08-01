# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.website_sale.controllers import main
from odoo.http import request
from odoo.exceptions import AccessDenied


class JtsWebsiteSale(main.WebsiteSale):

    # @http.route('/web/login', type='http', auth="none")
    # def web_login(self, redirect=None, **kw):
    #     print('login page')

    def values_postprocess(self, order, mode, values, errors, error_msg):
        res = super(JtsWebsiteSale, self).values_postprocess(order, mode, values, errors, error_msg)
        print('awasti ji'.center(100, '='))
        res_list = list(res)
        if values['mobile']:
            res_dict = res_list[0]
            mobile = values.get('mobile')
            res_dict.update({
                'mobile': mobile
            })
        res = tuple(res)
        return res
