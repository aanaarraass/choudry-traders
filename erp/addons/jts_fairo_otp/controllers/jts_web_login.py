# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers import main
from odoo.http import request
from odoo.exceptions import AccessDenied


class JtsWebHome(main.Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        print('login page')
        if request.httprequest.method == 'POST':
            enable_otp_login = False
            if enable_otp_login:
                return super().web_login(redirect)
            try:
                # uid = request.env['res.users'].sudo().search([('login', '=', request.params['login'])])
                uid = request.env['res.users'].sudo().search([('phone', '=', request.params['phone'])])
                # uid.sudo().reset_password(request.params['phone'])
                print('uid =========================================', uid)
                if uid:
                    login, passwd = request.params['phone'], request.params['phone']
                    # login, passwd = request.params['login'], request.params['password']
                    vals = dict(uid=uid.id, db=request.session.db, login=login, passwd=passwd)
                    uid.sudo().generate_otp_in_db()
                    return request.render("jts_fairo_otp.verify_otp_template", vals)
                else:
                    group_id = request.env.ref('base.group_portal')
                    # group_id = request.env.ref('base.group_public')
                    uid = request.env['res.users'].sudo().create({
                        'name': request.params['phone'],
                        'login': request.params['phone'],
                        'password': request.params['phone'],
                        'phone': request.params['phone'],
                        'email': request.params['phone'],
                        'groups_id': [(4, group_id.id)],
                    })
                    uid.sudo().generate_otp_in_db()
                    login, passwd = request.params['phone'], request.params['phone']
                    vals = dict(uid=uid.id, db=request.session.db, login=login, passwd=passwd)
                    return request.render("jts_fairo_otp.verify_otp_template", vals)
            except AccessDenied as e:
                pass
        return super().web_login(redirect)

    @http.route('/web/verify/otp', type='http', auth="public", csrf=False)
    def web_verify_otp(self, **kw):
        entered_otp, uid = request.params.get('otp'), request.params.get('uid')
        res = request.env['res.users'].browse(int(uid)).sudo().verify_otp(entered_otp)
        # res = request.env['res.users'].browse(2).sudo().verify_otp(entered_otp)
        login, passwd = request.params['login'], request.params['passwd']
        vals = dict(uid=uid, db=request.session.db, login=login, passwd=passwd,
                    wrong_login=False, otp_expire=False)
        if res == 1:
            try:
                uid = request.session.authenticate(request.session.db,
                                                   request.params['login'],
                                                   request.params['passwd'])
            except AccessDenied as e:
                vals.update(wrong_login=True)
                return request.render("jts_fairo_otp.verify_otp_template", vals)

            redirect = request.params['redirect']
            return request.redirect(self._login_redirect(uid, redirect=redirect))

        elif res == -1:
            return request.render("jts_fairo_otp.expire_otp_template", {})

        return request.render("jts_fairo_otp.wrong_otp_temp", {})

