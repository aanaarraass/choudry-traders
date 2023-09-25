from datetime import datetime

from odoo import models, fields, api,_


class MoblizationForm(models.Model):
    _name = 'moblization'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sr_no'

    date = fields.Date(track_visibility="Always", default=fields.date.today(), required=True)
    branch_id = fields.Many2one('res.branch', track_visibility="Always", required=True)
    staff_id = fields.Many2one('res.users', track_visibility="Always", required=True)
    superviosr_id = fields.Many2one('res.users', track_visibility="Always", required=True)
    sr_no = fields.Char(string='SR#', track_visibility="Always",copy=False,
                        default=lambda self: _('New'),required=True)
    moblization_line_ids = fields.One2many('moblization.line', 'moblization_id', track_visibility="Always")

    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancel')],
                             string="Status",default='draft')

    
    
    @api.model
    def create(self, vals):
        if vals.get('sr_no', _('New')) == _('New'):
            branch_id = vals['branch_id']
            vals['sr_no'] = self.env['ir.sequence'].next_by_code('mobilization.serial',branch_id) or _('New')
        return super(MoblizationForm, self).create(vals)

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.model
    def default_get(self, fields):
        result = super(MoblizationForm, self).default_get(fields)
        a = self.env.user.branch_id.id
        b = self.env.user.id
        result['branch_id'] = a
        result['staff_id'] = b
        return result


class MolizationFormLine(models.Model):
    _name = 'moblization.line'
    _description = 'Mobilization Contact Created'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sr_no = fields.Char(string='SR#', track_visibility="Always",copy=False,
                        default=lambda self: _('New'),required=True)
    name = fields.Char(track_visibility="Always", required=True)
    son_of = fields.Char(track_visibility="Always", required=True)
    area_id = fields.Many2one('area.area', track_visibility="Always", required=True)
    cell_no = fields.Char(string='Phone #', track_visibility="Always", required=True,default='+92')
    moblization_id = fields.Many2one('moblization', track_visibility="Always")
    date = fields.Date('Date')
    staff_id = fields.Many2one('res.users')
    branch_id = fields.Many2one('res.branch')
    superviosr_id = fields.Many2one('res.users', track_visibility="Always")


    @api.model
    def create(self, vals):
        if vals.get('sr_no', _('New')) == _('New'):
            vals['sr_no'] = self.env['ir.sequence'].next_by_code('mobilization.contact') or _('New')
        res = super(MolizationFormLine,self).create(vals)
        res['staff_id']=self.env.user.id
        if res.moblization_id:
            res['superviosr_id']=res.moblization_id.superviosr_id.id
            res['date'] = res.moblization_id.date
            res['branch_id']=res.moblization_id.branch_id.id

        return res




    _sql_constraints = [
        ('cell_nouniq', 'unique (cell_no)',
         'Mobile Number must be unique !'),
        ('sr_nouniq', 'unique (sr_no)',
         'Contact Serial must be unique !'),
    ]



class SmsTemplate(models.Model):
    _name = 'sms.mobilization.template'
    _description = 'Mobilization SMS Template'


    name = fields.Char('Name')
    body= fields.Text('SMS Body')



class SmsHistory(models.Model):
    _name = 'sms.history'
    _description = 'Mobilzation SMS History'


    moblization_contact_id = fields.Many2one('moblization.line')
    phone = fields.Char()
    body = fields.Text()
    sms_status = fields.Selection([('fail','Failed'),('done','Done')],string='SMS Status')
    sms_template_id = fields.Many2one('sms.mobilization.template')




class IrSequence(models.Model):
    _inherit = 'ir.sequence'


    def create_prefix_branch_code_wise(self,branch_id):
        if branch_id:
            branch = self.env['res.branch'].browse(branch_id)
            branch_code = branch.branch_code
            year= fields.datetime.now().year
            prefix = "%s/%s/" %(branch_code,year)
        return prefix

    @api.model
    def _next(self, sequence_date):
        if self.code == 'mobilization.serial':
            dynamic_prefix = self.create_prefix_branch_code_wise(sequence_date)
            self.prefix = dynamic_prefix
        return super(IrSequence, self)._next()