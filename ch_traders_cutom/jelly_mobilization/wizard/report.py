from datetime import datetime, date

from odoo import models, fields


class MobilizationWizard(models.TransientModel):
    _name = 'mobilization.report.wizard'
    _description = "This model is being used to get data on wizard"

    branch_id = fields.Many2one('res.branch', string="Branch")
    staff_id = fields.Many2one('res.users', string='Staff')
    area_id = fields.Many2one('area.area', string='Area')
    date_from = fields.Date('Date From',default=fields.date.today())
    date_to = fields.Date('Date To',default=fields.date.today())



    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.user.branch_id:
            res['branch_id'] = self.env.user.branch_id.id
        res['staff_id'] = self.env.user.id
        return res


    def make_domain(self):
        domain = []
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        if self.staff_id:
            domain.append(('staff_id', '=', self.staff_id.id))
        if self.area_id:
            domain.append(('area_id', '=', self.area_id.id))
        if self.date_from:
            domain.append(('date', '>', self.date_from))
        if self.date_to:
            domain.append(('date', '<', self.date_to))
        return domain


    def print_moblization_report(self):
        domain = self.make_domain()
        data = {
            'form_data': self.read()[0],
            'domain':domain
        }
        return self.env.ref('jelly_mobilization.mobilization_report').report_action(self,data=data)