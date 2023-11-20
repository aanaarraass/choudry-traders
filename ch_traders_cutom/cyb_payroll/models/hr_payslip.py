# -*- coding: utf-8 -*-


from dateutil.relativedelta import relativedelta
from pytz import timezone
import pytz

from odoo import _
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from datetime import date, datetime, time,timedelta
import calendar
min_time = time.min
max_time = time.max
my_calendar = calendar
class PayslipLeaveDate(models.Model):
    _name = 'payslip.leave.date'

    date_from = fields.Datetime('Date From')
    date_to = fields.Datetime('Date to')
    name = fields.Char()
    payslip_id = fields.Many2one('hr.payslip', string='payslip id')

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    _description = 'payroll_calculation'

    late_attendances_ids = fields.One2many('late.attendances.line', 'payslip_id', ondelete='cascade',
                                           string='Late Attendances')
    late_leave_attendances_ids = fields.One2many('late.leave.attendances.line', 'payslip_id', ondelete='cascade',
                                           string='Late Leave Attendances')
    absent_line_ids = fields.One2many('absent.line', 'payslip_id', ondelete='cascade', string='Absent Days')

    payslip_date_line = fields.One2many('payslip.leave.date', 'payslip_id', ondelete='cascade', string='Date Line')
    hr_leave_ids = fields.Many2many('hr.leave', string='Hr leaves')
    leaves_deducted = fields.Boolean(store=True)

    def create_leaves(self,date,type,hours):
        holiday_status_id_rec = self.env['hr.leave.type'].search([('code','=',type)])
        hr_leave_id = self.env['hr.leave'].create({
            'name': self.employee_id.name + ' Short Leave',
            'holiday_status_id': holiday_status_id_rec.id,
            'department_id': self.employee_id.department_id.id,
            'employee_id': self.employee_id.id,
            'request_date_from': date.date(),
            'request_date_to': date.date(),
            'date_from': date.replace(hour=9 + 5, minute=0, second=0),
            'date_to': date.replace(hour=9+hours + 5, minute=0, second=0),
            'number_of_days': 1 if hours>3 else 0.5,
            'number_of_hours_display': hours,
        })
        return  hr_leave_id
        # hr_leave_id.action_approve()
        # if hr_leave_id.state == 'validate1':
        #     hr_leave_id.action_validate()

    def make_leaves(self):
        leave_list = []
        j = self.late_attendances_ids.__len__() // 3
        self.worked_days_line_ids.filtered(lambda x:x.code=="LATE").unlink()
        absent_line = self.env['hr.payslip.worked_days'].create({
                'sequence': 10,
                'number_of_days': j,
                'number_of_hours': j * 8,
                'code': 'LATE',
                'contract_id': self.contract_id.id,
                'name': 'Late Attendance Deduction',
                'payslip_id':self.id,
                'amount': 223
            })
        self.worked_days_line_ids.filtered(lambda x: x.code == "ABSENT").unlink()
        if self.absent_line_ids.__len__()>0:
            absent_line = self.env['hr.payslip.worked_days'].create({
                'sequence': 11,
                'number_of_days': self.absent_line_ids.__len__()*2,
                'number_of_hours': (self.absent_line_ids.__len__()*2) * 8,
                'code': 'ABSENT',
                'contract_id': self.contract_id.id,
                'name': 'Absent Deduction',
                'payslip_id': self.id,
                'amount':222
            })
            # leave = self.create_leaves(self.late_attendances_ids[0].check_in,'FU',8)
            # leave_list.append(leave.id)

        k = self.late_leave_attendances_ids.__len__()
        for i in range(k):
            leave = self.create_leaves(self.late_leave_attendances_ids[0].check_in, 'SL', 3)
            leave_list.append(leave.id)

        self.write({
            'hr_leave_ids': [(6, 0, leave_list)],
            'leaves_deducted': True
        })

    def compute_sheet(self):
        if not self.leaves_deducted:
            self.action_deduct_leaves()
            penalty_leaves = self.hr_leave_ids.filtered(lambda x: x.holiday_status_id.id == 1 and x.state == 'validate')
            legal_leave_rec = self.worked_days_line_ids.filtered(lambda x:x.code=='GLOBAL')
            if legal_leave_rec:
                legal_leave_rec.number_of_days = legal_leave_rec.number_of_days +sum(penalty_leaves.mapped('number_of_days'))
                legal_leave_rec.number_of_hours =legal_leave_rec.number_of_hours+ sum(penalty_leaves.mapped('number_of_days')) * 8
            self.onchange_employee()
        res = super(HrPayslip, self).compute_sheet()
        return res

    def action_payslip_cancel(self):
        res = super(HrPayslip, self).action_payslip_cancel()
        for leave in self.hr_leave_ids:
            if leave.state=='validate' or leave.state=='validate1':
                leave.action_refuse()
        return res

    def action_payslip_draft(self):
        res = super(HrPayslip, self).action_payslip_draft()
        for leave in self.hr_leave_ids:
            leave.action_draft()
            leave.unlink()
        self.leaves_deducted = False
        return res

    def unlink(self):
        for leave in self.hr_leave_ids:
            leave.action_draft()
            leave.unlink()
        return super(HrPayslip, self).unlink()

    def action_deduct_leaves(self):
        m2m_leave_list = []
        for hr_date in self.payslip_date_line:
            diff = hr_date.date_to.date() - hr_date.date_from.date()
            days = diff.days+1
            holiday_status_id_rec = self.env['hr.leave.type'].browse(1)
            mapped_days = holiday_status_id_rec.get_employees_days(
                (self.employee_id).ids, hr_date.date_from.date())
            if self.employee_id:
                leave_days = mapped_days[self.employee_id.id][1]
                if leave_days['virtual_remaining_leaves']==0:
                    holiday_status_id = 4
                else:
                    holiday_status_id = 1
            hr_leave_id = self.env['hr.leave'].create({
                'name': hr_date.name,
                'holiday_status_id': holiday_status_id,
                'department_id': self.employee_id.department_id.id,
                'employee_id': self.employee_id.id,
                'request_date_from': hr_date.date_from.date(),
                'request_date_to': hr_date.date_to.date(),
                'date_from': hr_date.date_from.replace(hour=8+5, minute=0,second=0),
                'date_to': hr_date.date_to.replace(hour=16+5, minute=0,second=0),
                'number_of_days': days,
                'number_of_hours_display': days*8,
            })
            hr_leave_id.action_approve()
            if hr_leave_id.state=='validate1':
                hr_leave_id.action_validate()
            m2m_leave_list.append(hr_leave_id.id)

        self.write({
            'hr_leave_ids': [(6, 0, m2m_leave_list)],
            'leaves_deducted':True
        })

    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        :returns: a list of dict containing the worked days values that should be applied for the given payslip
        """
        res = []
        # super(WorkedDayOvertime,self)._get_worked_day_lines()

        def day_name_cal(day):
            if day == '0':
                return "Monday"
            elif day == '1':
                return 'Tuesday'
            elif day == '2':
                return 'Wednesday'
            elif day == '3':
                return 'Thursday'
            elif day == '4':
                return 'Friday'
            elif day == '5':
                return 'Saturday'
            elif day == '6':
                return 'Sunday'

        total_time=0
        attendance_duration=0
        attendance_days=0
        day_count = 0
        date_from_cont = fields.Datetime.from_string(self.contract_id.date_start)
        date_from_cont = str(date_from_cont)
        date_to_cont = fields.Datetime.from_string(self.contract_id.date_end)
        date_to_cont = str(date_to_cont)
        days_of_schedule = []

        for days in self.contract_id.resource_calendar_id.attendance_ids:
            days_of_schedule.append(str(day_name_cal(days.dayofweek)))
        leaves = {}
        calendar = self.contract_id.resource_calendar_id
        tz = timezone(calendar.tz)
        day_from = datetime.strptime(str(self.date_from), "%Y-%m-%d")
        day_to = datetime.strptime(str(self.date_to), "%Y-%m-%d")
        day_leave_intervals = self.contract_id.employee_id.list_leaves(day_from, day_to,
                                                                       calendar=self.contract_id.resource_calendar_id)
        for day, hours, leave in day_leave_intervals:
            holiday = leave.holiday_id
            current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                'name': holiday.holiday_status_id.name or _('Global Leaves'),
                'sequence': 5,
                'code': holiday.holiday_status_id.code or 'GLOBAL',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': self.contract_id.id,
            })
            current_leave_struct['number_of_hours'] += hours
            work_hours = calendar.get_work_hours_count(
                tz.localize(datetime.combine(day, min_time)),
                tz.localize(datetime.combine(day, max_time)),
                compute_leaves=False,
            )
            if work_hours:
                current_leave_struct['number_of_days'] += hours / work_hours

        day_count = (self.date_to - self.date_from).days + 1
        for single_date in [d for d in (self.date_from + timedelta(n) for n in range(day_count)) if d <= self.date_to]:
            date = single_date
            attendance = self.env['hr.attendance'].search(
                [('employee_id', '=', self.employee_id.id), ('check_in', '>=', date),
                 ('check_in', '<=', date)])
            if attendance:
                attendance_days +=1
            else:

                # month_day = calendar.day_name[single_date.weekday()]
                month_day = my_calendar.day_name[date.weekday()]
                # if month_day != 'Sunday':
                #     attendance_days +=1
        upaid_leaves_days = 0
        for leave in self.env['hr.leave'].search([('request_date_from', '>=', self.date_from),
                                                      ('request_date_to', '<=', self.date_to),
                                                      ('employee_id', '=', self.employee_id.id),
                                                      ('state', '=', 'validate'),('holiday_status_id','=',4)]):
            upaid_leaves_days += leave.number_of_days_display

        if upaid_leaves_days:
            res.append({
            'sequence': 10,
            'number_of_days': upaid_leaves_days,
            'number_of_hours': upaid_leaves_days*8,
            'code':'UNPAID',
            'contract_id': self.contract_id.id,
            'name':'Unpaid Leaves',
        })
        paid_leaves_days = 0
        for leave in self.env['hr.leave'].search([('request_date_from', '>=', self.date_from),
                                                  ('request_date_to', '<=', self.date_to),
                                                  ('employee_id', '=', self.employee_id.id),
                                                  ('state', '=', 'validate'), ('holiday_status_id', '=', 1)]):
            paid_leaves_days += leave.number_of_days_display

        if paid_leaves_days:
            res.append({
                'sequence': 9,
                'number_of_days': paid_leaves_days,
                'number_of_hours': paid_leaves_days * 8,
                'code': 'PAID',
                'contract_id': self.contract_id.id,
                'name': 'Paid Leaves',
            })
        # sick_leaves_hours = 0
        # for leave in self.env['hr.work.entry'].search([('date_start', '>=', self.date_from),
        #                                               ('date_stop', '<=', self.date_to),
        #                                               ('employee_id', '=', self.employee_id.id),
        #                                               ('work_entry_type_id', '=', 6)]):
        #     sick_leaves_hours += leave.duration
        # res.append({
        #     'sequence': 6,
        #     'work_entry_type_id': self.env['hr.work.entry.type'].search([('id', '=', 6)]).id,
        #     'number_of_days': sick_leaves_hours/8,
        #     'number_of_hours': sick_leaves_hours,
        #     'code':'LEAVE110'
        # })
        # paid_leaves_hours = 0
        # for leave in self.env['hr.work.entry'].search([('date_start', '>=', self.date_from),
        #                                                ('date_stop', '<=', self.date_to),
        #                                                ('employee_id', '=', self.employee_id.id),
        #                                                ('work_entry_type_id', '=', 7)]):
        #     paid_leaves_hours += leave.duration
        #
        # res.append({
        #     'sequence': 6,
        #     'work_entry_type_id': self.env['hr.work.entry.type'].search([('id', '=', 7)]).id,
        #     'number_of_days': paid_leaves_hours / 8,
        #     'number_of_hours': paid_leaves_hours,
        #     'code': 'LEAVE120'
        # })

        res.append({
            'sequence': 5,
            'number_of_days': attendance_days,
            'number_of_hours': attendance_duration,
            'name':'Working Days',
            'code':'WORK100',
            'contract_id':self.contract_id.id,
        })

        # res.extend(leaves.values())
        # self.ensure_one()
        # contract = self.contract_id
        # if contract.resource_calendar_id:
        #     # res = self._get_worked_day_lines_values(domain=domain)
        #     if not check_out_of_contract:
        #         return res
        #
        #     # If the contract doesn't cover the whole month, create
        #     # worked_days lines to adapt the wage accordingly
        #     out_days, out_hours = 0, 0
        #     reference_calendar = self._get_out_of_contract_calendar()
        #     if self.date_from < contract.date_start:
        #         start = fields.Datetime.to_datetime(self.date_from)
        #         stop = fields.Datetime.to_datetime(contract.date_start) + relativedelta(days=-1, hour=23, minute=59)
        #         out_time = reference_calendar.get_work_duration_data(start, stop, compute_leaves=False)
        #         out_days += out_time['days']
        #         out_hours += out_time['hours']
        #     if contract.date_end and contract.date_end < self.date_to:
        #         start = fields.Datetime.to_datetime(contract.date_end) + relativedelta(days=1)
        #         stop = fields.Datetime.to_datetime(self.date_to) + relativedelta(hour=23, minute=59)
        #         out_time = reference_calendar.get_work_duration_data(start, stop, compute_leaves=False)
        #         out_days += out_time['days']
        #         out_hours += out_time['hours']
        #
        #     if out_days or out_hours:
        #         work_entry_type = self.env.ref('hr_payroll.hr_work_entry_type_out_of_contract')
        #         res.append({
        #             'sequence': work_entry_type.sequence,
        #             'work_entry_type_id': work_entry_type.id,
        #             'number_of_days': out_days,
        #             'number_of_hours': out_hours,
        #         })
        return res
    def _action_create_account_move(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')

        # Add payslip without run
        payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        # Map all payslips by structure journal and pay slips month.
        # {'journal_id': {'month': [slip_ids]}}
        slip_mapped_data = {slip.struct_id.journal_id.id: {fields.Date().end_of(slip.date_to, 'month'): self.env['hr.payslip']} for slip in payslips_to_post}
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip

        for journal_id in slip_mapped_data: # For each journal_id.
            for slip_date in slip_mapped_data[journal_id]: # For each month.
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                date = slip_date
                move_dict = {
                    'narration': '',
                    'ref': date.strftime('%B %Y'),
                    'journal_id': journal_id,
                    'date': date,
                }

                for slip in slip_mapped_data[journal_id][slip_date]:
                    move_dict['narration'] += slip.number or '' + ' - ' + slip.employee_id.name or ''
                    move_dict['narration'] += '\n'
                    slip_lines = slip._prepare_slip_lines(date, line_ids)
                    line_ids.extend(slip_lines)

                for line_id in line_ids: # Get the debit and credit sum.
                    debit_sum += line_id['debit']
                    credit_sum += line_id['credit']
                    line_id['partner_id'] = self.employee_id.address_home_id.id

                # The code below is called if there is an error in the balance between credit and debit sum.
                if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    slip._prepare_adjust_line(line_ids, 'credit', debit_sum, credit_sum, date)
                elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    slip._prepare_adjust_line(line_ids, 'debit', debit_sum, credit_sum, date)

                # Add accounting lines in the move
                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                move = self._create_account_move(move_dict)
                for slip in slip_mapped_data[journal_id][slip_date]:
                    slip.write({'move_id': move.id, 'date': date})
        return True

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def onchange_employee(self):
        result = super(HrPayslip, self).onchange_employee()
        self.input_line_ids = False
        self.payslip_date_line = False
        self.late_attendances_ids = False
        self.late_leave_attendances_ids = False
        attendance_list = []
        attendance_leave_list = []
        o2m_list = []
        attendances = self.env['hr.attendance'].search(
            [('employee_id', '=', self.employee_id.id), ('check_in', '>=', self.date_from),
             ('check_in', '<=', self.date_to)])
        res_calendar = self.env['resource.calendar'].search([('id', '=', self.employee_id.resource_calendar_id.id)])
        if res_calendar:
            j = 0
            for days in res_calendar.attendance_ids:
                day = days.dayofweek
                name_of_day = dict(days.fields_get(allfields=['dayofweek'])['dayofweek']['selection'])[days.dayofweek]
                for attendance in attendances:
                    at_day = attendance.check_in.strftime("%A")
                    if at_day == name_of_day:
                        similar = at_day
                        user_tz = pytz.timezone(self.env.get('tz') or self.env.user.tz)
                        pak_time = pytz.utc.localize(attendance.check_in).astimezone(user_tz)

                        user_hour = pak_time.hour
                        user_min = pak_time.minute
                        user_float_time = user_hour + (user_min / 60)
                        grace = res_calendar.grace_time
                        user_time = round(user_float_time, 2)
                        schedule = (days.hour_from + grace)
                        if user_time > schedule:
                            if user_time < 9.5:
                                attendance_list.append((0, 0, {
                                    'check_in': attendance.check_in,
                                    'check_out': attendance.check_out,
                                    'hours': attendance.worked_hours,
                                    'date': attendance.check_in,
                                    'payslip_id': self.id,
                                }))
                            else:
                                attendance_leave_list.append((0, 0, {
                                    'check_in': attendance.check_in,
                                    'check_out': attendance.check_out,
                                    'hours': attendance.worked_hours,
                                    'date': attendance.check_in,
                                    'payslip_id': self.id,
                                }))
                            j += 1
                            if j % 2 == 0:
                                o2m_list.append((0, 0, {
                                    'date_from': attendance.check_in,
                                    'date_to': attendance.check_out,
                                    'name': 'Late Attendance Penalty'
                                }))
        #absent days
        absent_list = []
        self.absent_line_ids = False
        num_of_days = (self.date_to - self.date_from).days + 1
        all_days_of_calendar = []
        for days in res_calendar.attendance_ids:
            name_of_day = dict(days.fields_get(allfields=['dayofweek'])['dayofweek']['selection'])[days.dayofweek]
            all_days_of_calendar.append(name_of_day)
        for i in range(0, num_of_days):
            date_from = self.date_from + timedelta(days=i)
            date_time_from = datetime.strptime(date_from.strftime('%Y%m%d'), '%Y%m%d')
            day_min = datetime.combine(date_time_from, date_time_from.time().min)
            day_max = datetime.combine(date_time_from, date_time_from.time().max)
            day_attendances = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id),
                                                                   ('check_in', '>=', day_min),
                                                                   ('check_in', '<=', day_max)])
            if not day_attendances:
                at_day = day_min.strftime("%A")
                if at_day in all_days_of_calendar:
                    today_date = day_min.date()
                    today_start = fields.Datetime.to_string(today_date)
                    today_end = fields.Datetime.to_string(today_date + relativedelta(hours=23, minutes=59, seconds=59))
                    holidays = self.env['hr.leave'].sudo().search([
                        ('employee_id', '=', self.employee_id.id),
                        ('state', 'not in', ['cancel', 'refuse']),
                        ('date_from', '<=', today_end),
                        ('date_to', '>=', today_start),
                    ])
                    if not holidays:
                        month_day = my_calendar.day_name[today_date.weekday()]
                        if month_day != 'Sunday':
                            absent_list.append((0, 0, {
                                'absent_date': date_time_from
                            }))
                # calendar_day = res_calendar.attendance_ids.filtered(
                #     lambda x: x.dayofweek == str(date_from.weekday()))
                # calendar_time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(calendar_day.hour_from * 60, 60))
                # calendar_time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(calendar_day.hour_to * 60, 60))
                # time_from = datetime.strptime(calendar_time_from, '%H:%M').time()
                # date_time_from = datetime.combine(date_from, time_from)
                # time_to = datetime.strptime(calendar_time_to, '%H:%M').time()
                # date_time_to = datetime.combine(date_from, time_to)
                # holidays = self.env['hr.leave'].search([
                #     ('employee_id', '=', self.employee_id.id),
                #     ('date_from', '<=', str(day_max)),
                #     ('date_to', '>=', str(day_min)), ('state', '=', 'validate')
                # ])
                # if not holidays:
                #     o2m_list.append((0, 0, {
                #         'date_from': date_time_from,
                #         'date_to': date_from + timedelta(days=1),
                #         'name': 'Monday off Penalty'
                #     }))
        sales_incentive = self.env['sale.incentive'].search([('salesman_id','=',self.employee_id.id),
                                                             ('date','>=',self.date_from),('date','<=',self.date_to)])
        cash_type = sum(sales_incentive.filtered(lambda x:x.sale_type=='cash').mapped('commission_amount'))
        lease_type = sum(sales_incentive.filtered(lambda x:x.sale_type=='lease').mapped('commission_amount'))
        recovery_incentive = 0
        if self.contract_id.recovery_incentive_id.recovery_incentive>0:
            lease_sale = self.env['lease.sale'].search([('recovery_officer_id','=',self.employee_id.id),
                                                                 ('lease_date','>=',self.date_from),('lease_date','<=',self.date_to),('state','=','done')])
            lease_sale_amount = sum(lease_sale.mapped('sale_total'))
            recovery_incentive = round(self.contract_id.recovery_incentive_id.recovery_incentive/100 *lease_sale_amount,2)
        input_line_ids = [
            (0, 0, {
                'name': 'Cash Sale Incentive',
                'amount': cash_type,
                'contract_id':self.contract_id.id,
                'code':'CSI',
            }),
            (0, 0, {
                'name': 'Lease Sale Incentive',
                'amount': lease_type,
                'contract_id': self.contract_id.id,
                'code': 'LSI',
            }),
            (0, 0, {
                'name': 'Recovery Office Sale Incentive',
                'amount': recovery_incentive,
                'contract_id': self.contract_id.id,
                'code': 'RSI',
            })
        ]
        self.update({
            'late_attendances_ids': attendance_list,
            'late_leave_attendances_ids': attendance_leave_list,
            'absent_line_ids': absent_list,
            'input_line_ids':input_line_ids
        })

        self.write({
            'payslip_date_line': o2m_list
        })
        return

class AmountPayslipLines(models.Model):
    _inherit = 'hr.payslip.worked_days'

    amount = fields.Float(compute='_compute_amount')

    @api.depends('number_of_hours', 'payslip_id')
    def _compute_amount(self):

        for worked_days in self:
            if not worked_days.contract_id:
                worked_days.amount = 0
                continue
            per_day = worked_days.contract_id.wage /30
            worked_days.amount =  worked_days.number_of_days * per_day
            # day_from = datetime.strptime(str(worked_days.payslip_id.date_from), "%Y-%m-%d")-timedelta(days=1)
            # day_to = datetime.strptime(str(worked_days.payslip_id.date_to), "%Y-%m-%d")
            # nb_of_days = (day_to - day_from).days
            # dates = (day_from + timedelta(idx + 1)
            #          for idx in range((day_to - day_from).days))
            # res = 0
            # for day in dates:
            #     if day.weekday() < self.payslip_id.employee_id.resource_calendar_id.attendance_ids.__len__():
            #        res+=1
            # # res = sum(1 for day in dates if day.weekday() < self.payslip_id.employee_id.resource_calendar_id.attendance_ids.__len__())
            # calendar_time = res*9
            # if calendar_time:
            #     basic_wage = worked_days.contract_id.wage
            #     hourly_wages = basic_wage / calendar_time
            #     worked_days.amount = round(worked_days.number_of_hours) * hourly_wages
            # else:
            #     worked_days.amount = 0



class LateAttendancesLine(models.Model):
    _name = 'late.attendances.line'
    _description = 'LateAttendancesLine'

    date = fields.Datetime('Date')
    check_in = fields.Datetime('Check In')
    check_in_float = fields.Float('Float In')
    check_out = fields.Datetime('Check Out')
    hours = fields.Float('Hours')

    payslip_id = fields.Many2one('hr.payslip', string='Payslip_id')

class LateLeaveAttendancesLine(models.Model):
    _name = 'late.leave.attendances.line'
    _description = 'LateAttendancesLine'

    date = fields.Datetime('Date')
    check_in = fields.Datetime('Check In')
    check_in_float = fields.Float('Float In')
    check_out = fields.Datetime('Check Out')
    hours = fields.Float('Hours')

    payslip_id = fields.Many2one('hr.payslip', string='Payslip_id')


class AbsentLine(models.Model):
    _name = 'absent.line'

    absent_date = fields.Date(string='Absent Date')
    payslip_id = fields.Many2one('hr.payslip', string='Payslip_id')


class HRContract(models.Model):
    _inherit = 'hr.contract'

    # recovery_incentive = fields.Float('Recovery Office Sale Incentive(%)')
    recovery_incentive_id = fields.Many2one('recovery.incentive',string='Recovery Office Sale Incentive(%)')



class RecoveryIncentive(models.Model):
    _name = 'recovery.incentive'

    name = fields.Char(string='Incentive Name')
    recovery_incentive = fields.Float('Recovery Office Sale Incentive(%)')

