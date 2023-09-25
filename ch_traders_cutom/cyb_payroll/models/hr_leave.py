import datetime
from datetime import timezone

from odoo import models,_,fields
from odoo.exceptions import UserError,ValidationError
import pytz

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    current_quarter = fields.Integer()

    def action_approve(self):
        holiday_status = self.env['hr.leave.type'].search([('code','=','PAIDOFF')])
        if self.number_of_days>3:
            raise ValidationError('Only 3 leaves can be taken in on quarter')
        current_date = self.request_date_from
        current_quarter = (current_date.month - 1) // 3 + 1
        leaves = self.search([('current_quarter','=',current_quarter),('state','=','validate'),('employee_id','=',self.employee_id.id),
                              ('holiday_status_id','=',holiday_status.id)])
        if leaves:
            leaves_sum = sum(leaves.mapped('number_of_days'))
            if leaves_sum+self.number_of_days >3:
                raise ValidationError('Only 3 leaves can be taken in on quarter')
        self.current_quarter = current_quarter
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below
        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_('Time off request must be confirmed ("To Approve") in order to approve it.'))

        current_employee = self.env.user.employee_id
        self.filtered(lambda hol: hol.validation_type == 'both').write(
            {'state': 'validate1', 'first_approver_id': current_employee.id})

        # Post a second message, more verbose than the tracking message
        for holiday in self.filtered(lambda holiday: holiday.employee_id.user_id):
            user_tz = timezone(holiday.tz)
            utc_tz = pytz.utc.localize(holiday.date_from).astimezone(user_tz)
            holiday.message_post(
                body=_(
                    'Your %(leave_type)s planned on %(date)s has been accepted',
                    leave_type=holiday.holiday_status_id.display_name,
                    date=utc_tz.replace(tzinfo=None)
                ),
                partner_ids=holiday.employee_id.user_id.partner_id.ids)

        self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        if not self.env.context.get('leave_fast_create'):
            self.activity_update()
        return True

