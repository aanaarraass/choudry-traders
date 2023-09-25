from datetime import timedelta

from odoo import models, fields


class LeaseTransaction(models.TransientModel):
    _name = 'lease.transaction'
    _description = "This model is being used to get data on wizard Lease Report"

    branch_id = fields.Many2many('res.branch', string='Branch')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    def get_month_range(self, start_date, end_date):
        month_range = []
        current_date = start_date
        last_month = None
        while current_date <= end_date:
            if last_month != current_date.month:
                month_range.append((current_date.month, current_date.year))
                last_month = current_date.month
            current_date += timedelta(days=1)

        return month_range

    def get_sale_item_qty(self,branch_id,date):
        a=1
        print('sdf')
    def get_date_range(self, start_date, end_date):
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)
        return date_range

    def print_lease_trancation(self):
        domain = []
        if self.branch_id:
            ids = list([x.id for x in self.branch_id])
            domain.append(('branch_id', '=', ids))
        if self.date_from:
            domain.append(('lease_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('lease_date', '<=', self.date_to))

        data = {
            'domain': domain,
           'date_from':self.date_from,
            'date_to':self.date_to,

        }
        return self.env.ref('lease_reporting.lease_sale_tracncation_report').report_action(self, data=data)

    def print_lease_summary(self):
        domain = []
        if self.branch_id:
            ids = list([x.id for x in self.branch_id])
            domain.append(('branch_id', 'in', ids))
        if self.date_from:
            domain.append(('lease_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('lease_date', '<=', self.date_to))
        date_range = self.get_date_range(self.date_from, self.date_to)

        data = {
            'domain': domain,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'date_range':date_range,
        }

        return self.env.ref('lease_reporting.lease_branch_wise_report').report_action(self, data=data)

    def print_lease_officer_wise(self):
        domain = []
        if self.branch_id:
            ids = list([x.id for x in self.branch_id])
            domain.append(('branch_id', 'in', ids))
        if self.date_from:
            domain.append(('lease_date', '>', self.date_from))
        if self.date_to:
            domain.append(('lease_date', '<', self.date_to))

        data = {
            'domain': domain,
        }

        return self.env.ref('lease_reporting.officer_wise_sale_summary').report_action(self, data=data)

    def print_officer_wise_over_due(self):
        domain = []
        if self.branch_id:
            ids = list([x.id for x in self.branch_id])
            domain.append(('branch_id', '=', ids))
        if self.date_from:
            domain.append(('lease_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('lease_date', '<=', self.date_to))
        html=''

        lease_ids= self.env['lease.sale'].search(domain)
        branch_id = lease_ids.mapped('branch_id')
        for branch in branch_id:
            br_no_lease = 0
            br_lease_sum = 0
            br_lease_recved = 0
            br_lease_recable = 0
            br_lease_per_month = 0
            br_lease_short = 0
            html+='<tr>'
            html+='<th colspan="3" style="background-color: #dddddd">'
            html+=str(branch.name)
            html+='</th>'
            html += '<th colspan="6">'
            html += '</th>'
            html+='</tr>'
            html+='<tr> <th colspan="1">Code</th> <th colspan="1">No.of Lease</th> <th style="width: 18%">Recovery Officer</th> <th colspan="1">Lease Amount</th> <th colspan="1">Received Amount</th> <th colspan="1">Receivable Amount</th> <th colspan="1">Per Month Inst.</th> <th colspan="1">Last Recovered</th> <th colspan="1">Short Amount</th> </tr>'
            branch_lease= lease_ids.filtered(lambda x:x.branch_id.id == branch.id)
            recover_officer_id= branch_lease.mapped('recovery_officer_id')
            for officer in recover_officer_id:
                lease_of_recovery_officer = branch_lease.filtered(lambda o:o.recovery_officer_id.id == officer.id)
                html+='<tr>'
                html+='<td></td>'
                html+='<td>'
                html+=str(len(lease_of_recovery_officer))
                br_no_lease+=len(lease_of_recovery_officer)
                html+='</td>'
                html += '<td>'
                html += str(officer.name)
                html += '</td>'
                lease_sum = 0
                lease_recived_amount = 0
                lease_recivable_amount = 0
                per_month_instalment = 0

                for lease in lease_of_recovery_officer:
                    lease_sum+=lease.sale_total-lease.sale_return_total
                    lease_recived_amount+=lease.total_paid
                    lease_recivable_amount+=lease.total_receivable
                    per_month_instalment+=lease.installment_ids[0].amount
                short_amount = lease_sum-lease_recived_amount
                html+='<td>'
                html+=str(lease_sum)
                br_lease_sum+=lease_sum
                html+='</td>'
                html += '<td>'
                html += str(lease_recived_amount)
                br_lease_recved+=lease_recived_amount
                html += '</td>'
                html += '<td>'
                html += str(lease_recivable_amount)
                br_lease_recable+=lease_recivable_amount
                html += '</td>'
                html += '<td>'
                html += str(per_month_instalment)
                br_lease_per_month+=per_month_instalment
                html += '</td>'
                html += '<td>'
                html += str(' ')
                html += '</td>'
                html += '<td>'
                html += str(short_amount)
                br_lease_short+=short_amount
                html += '</td>'
                html+='</tr>'
            html+='<tr>'
            html+='<th>'
            html+='</th>'
            html += '<th>'
            html+=str(br_no_lease)
            html += '</th>'
            html += '<th>'
            html += 'Total'
            html += '</th>'
            html += '<th>'
            html += str(br_lease_sum)
            html += '</th>'
            html += '<th>'
            html += str(br_lease_recved)
            html += '</th>'
            html += '<th>'
            html += str(br_lease_recable)
            html += '</th>'
            html += '<th>'
            html += str(br_lease_per_month)
            html += '</th>'
            html += '<th>'
            html += str('')
            html += '</th>'
            html += '<th>'
            html += str(br_lease_short)
            html += '</th>'
            html+='</tr>'



        data = {
             'date_from': self.date_from,
            'date_to': self.date_to,
            'html':html,
        }
        return self.env.ref('lease_reporting.officer_over_due_summary_report_id').report_action(self, data=data)

    def print_lease_month_wise_summary(self):
        domain = []
        if self.branch_id:
            ids = list([x.id for x in self.branch_id])
            domain.append(('branch_id', 'in', ids))
        if self.date_from:
            domain.append(('lease_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('lease_date', '<=', self.date_to))
        month_range = self.get_month_range(self.date_from, self.date_to)
        data = {
            'domain': domain,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'month_range': month_range,
        }
        return self.env.ref('lease_reporting.lease_summary_month_wise_report').report_action(self, data=data)
    def get_year_range(self, start_date, end_date):
        year_range = []
        current_date = start_date
        last_year = None

        while current_date <= end_date:
            if last_year != current_date.year:
                year_range.append(current_date.year)
                last_year = current_date.year
            current_date += timedelta(days=1)

        return year_range

    def print_lease_year_wise_summary(self):
        domain = []
        if self.branch_id:
            ids = list([x.id for x in self.branch_id])
            domain.append(('branch_id', 'in', ids))
        if self.date_from:
            domain.append(('lease_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('lease_date', '<=', self.date_to))
        year_range = self.get_year_range(self.date_from, self.date_to)

        data = {
            'domain': domain,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'year_range': year_range,
        }

        return self.env.ref('lease_reporting.lease_summary_year_wise_report').report_action(self, data=data)





