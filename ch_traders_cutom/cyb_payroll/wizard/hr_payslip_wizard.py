# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HrPyrollWizardLine(models.TransientModel):
    _name = "hr.payslip.wizard.line"


    wizard_id =fields.Many2one('hr.payslip.wizard')
    leave_type_id = fields.Many2one('hr.leave.type')
    count = fields.Float(string="Count",required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    @api.onchange('date_from','date_to')
    def onchange_dates(self):
        if self.date_from and self.date_to:
            diff = self.date_to - self.date_from
            self.count = diff.days +1


class HrPyrollInheritWizard(models.TransientModel):
    _name = 'hr.payslip.wizard'

    monday_count = fields.Integer('Late Mondays')
    late_mondays = fields.Float('Monday Off Leaves')
    late_count = fields.Integer('Total Late Attendances')
    leave_type_ids = fields.One2many('hr.payslip.wizard.line','wizard_id')
    allcount = fields.Float(string="Late Attendance Leaves")
    leaves_count = fields.Float(string="Total Leaves Count")
    hr_leave_ids = fields.Many2many('hr.leave', string='Leaves of Month')


    @api.model
    def default_get(self, default_fields):
        values = super().default_get(default_fields)
        payslip = self.env['hr.payslip'].browse(self._context.get('active_id'))
        m2m_list = []
        if payslip:
            month_leaves = self.env['hr.leave'].search([('employee_id', '=', payslip.employee_id.id),
                                                        ('date_from', '>=', payslip.date_from),
                                                        ('date_to', '<=', payslip.date_to)])
            for leave in month_leaves:

                m2m_list.append(leave.id)
        values['late_count'] = payslip.late_attendances_ids.__len__()
        values['monday_count'] = payslip.monday_line_ids.__len__()
        values['allcount'] = values['late_count'] / 2
        values['late_mondays'] = values['monday_count'] * 2
        values['leaves_count'] = values['late_count'] / 2 + values['monday_count'] * 2
        values['hr_leave_ids'] = [(6, 0, m2m_list)]
        return values


    def generate_leave(self):
        if self.leave_type_ids:
            if sum(self.leave_type_ids.mapped('count')) > self.leaves_count :
                raise ValidationError(_("Total Leaves should not be greater than leave count."))
            else:
                for leave in self.leave_type_ids:
                    self.env['hr.leave'].create({
                        'name': 'Penalty',
                        'holiday_status_id': leave.leave_type_id.id,
                        'department_id': self.env['hr.payslip'].browse(self._context.get('active_id')).employee_id.department_id.id,
                        'employee_id': self.env['hr.payslip'].browse(self._context.get('active_id')).employee_id.id,
                        'date_from': leave.date_from,
                        'date_to': leave.date_to,
                        'number_of_days': leave.count,
                    })

        return
