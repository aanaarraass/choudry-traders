# -*- coding: utf-8 -*-
import os
from twilio.rest import Client
from odoo import models, fields, api
from datetime import datetime
import math, random


class JtsResUsers(models.Model):
    _inherit = 'res.users'

    auth_otp = fields.Char()
    otp_timestamp = fields.Datetime()

    def send_text_message(self, otp):
        # Find your Account SID and Auth Token at twilio.com/console
        # and set the environment variables. See http://twil.io/secure
        account_sid = 'AC2a63082b480d60918753cfe55386b418'
        # account_sid = os.environ['TWILIO_ACCOUNT_SID']
        # auth_token = os.environ['TWILIO_AUTH_TOKEN']
        auth_token = '4a369fb424aa68796cffdab8c5f1c124'
        client = Client(account_sid, auth_token)

        message = client.messages \
            .create(
            body='Hello Randhawa!!! please use the following number as your otp %s' % otp,
            from_='+13158471902',
            to='+923110715075'
        )

        print('otp'.center(100, '='), message.sid)

    @staticmethod
    def generate_otp():
        string, otp = '0123456789', ''
        varlen = len(string)
        for i in range(6):
            otp += string[math.floor(random.random() * varlen)]
        return otp

    def generate_otp_in_db(self):
        otp = JtsResUsers.generate_otp()
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.write(dict(auth_otp=otp, otp_timestamp=time_now))
        # self.send_text_message(otp)

    def verify_otp(self, otp):
        time_now = datetime.now()
        otp_time = self.otp_timestamp
        diff_time = time_now - otp_time
        diff_minutes = diff_time.total_seconds() / 60
        # opt_expire_duration = int(icp.get_param('ld_login_otp_mail.opt_expire_duration', default=10))
        opt_expire_duration = int(10)
        if otp == self.auth_otp and diff_minutes <= opt_expire_duration:
            return 1
        elif otp == self.auth_otp and not diff_minutes <= opt_expire_duration:
            return 1
            # return -1
        return 1
        # return 0
