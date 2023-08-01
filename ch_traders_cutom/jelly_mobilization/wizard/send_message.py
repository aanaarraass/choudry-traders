from odoo import fields, models, api


class SendMessage(models.TransientModel):
    _name = 'send.message'
    _description = 'Send Message'

    branch_id = fields.Many2one('res.branch', string="Branch")
    staff_id = fields.Many2one('res.users',string='Staff')
    area_id = fields.Many2one('area.area',string='Area')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    message_id = fields.Many2one('sms.mobilization.template',string='Message Template')
    message_body = fields.Text('Message')
    moblization_contact_ids = fields.Many2many('moblization.line')




    @api.onchange('message_id')
    def get_message_body(self):
        for rec in self:
            rec.message_body = rec.message_id.body

    @api.onchange('branch_id','staff_id','area_id','date_from','date_to')
    def get_moblization_contacts(self):
        self.moblization_contact_ids = False
        if not self.branch_id:
            return
        domain = []
        domain.append(('branch_id','=',self.branch_id.id))
        if self.staff_id:
            domain.append(('staff_id','=',self.staff_id.id))
        if self.area_id:
            domain.append(('area_id','=',self.area_id.id))
        if self.date_from:
            domain.append(('date','>',self.date_from))
        if self.date_to:
            domain.append(('date','<',self.date_to))
        contacts = self.env['moblization.line'].search(domain)
        self.moblization_contact_ids = contacts


    def post_message(self):
        odoobot = self.env.ref('base.partner_root')
        body = self.message_body
        for line in self.moblization_contact_ids:
                sms_history = self.env['sms.history'].create({
                    'moblization_contact_id': line.id,
                    'phone' : line.cell_no,
                    'body' : body,
                    'sms_template_id': self.message_id.id
                })
                line.message_post(body=body,
                                  message_type='comment',
                                  subtype_xmlid='mail.mt_note',
                                  author_id=odoobot.id)
                # import requests

                # url = "https://connect.jazzcmt.com/sendsms_url.html?Username=0300xxxxxx&Password" \
                #       " = xxxxxx & From =0345794115 & To = 0300xxxxxxx & Message = MESSAGE" \
                #       " & Identifier = xxxxxxx" \
                #       " & UniqueId = xxxxxxx & ProductId = 35146465" \
                #       " & Channel = xxxxxxx13213 " \
                #       "& TransactionId = xxxxxxx21321"
                #
                # payload = {}
                # headers = {}
                #
                # response = requests.request("POST", url, headers=headers, data=payload)
                #
                # print(response.text)
