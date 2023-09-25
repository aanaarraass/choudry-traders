import pytz
from dateutil.relativedelta import relativedelta
from odoo import models,api,fields


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    is_work_entry = fields.Boolean()

    @api.model
    def set_work_time(self):
        attendances = self.browse(self._context.get('active_ids'))
        if not attendances:
            now = fields.Datetime.now()
            now_utc = pytz.utc.localize(now)
            tz = pytz.timezone('Asia/Karachi')
            now_tz = now_utc.astimezone(tz)
            start_tz = now_tz + relativedelta(hour=0, minute=0, second=0, microsecond=0)
            start_naive = start_tz.astimezone(pytz.utc).replace(tzinfo=None)
            end_tz = start_tz + relativedelta(hour=23, minute=59, second=59, microsecond=0)
            end_naive = end_tz.astimezone(pytz.utc).replace(tzinfo=None)
            attendances = self.env['hr.attendance'].search([
                ('check_in', '>=', start_naive), ('check_in', '<=', end_naive),
            ])
        for rec in attendances:
            if not rec.is_work_entry:
                if rec.check_in and rec.check_out:
                    self.env['hr.work.entry'].sudo().create({'employee_id': rec.employee_id.id,
                                                             'date_start': rec.check_in,
                                                             'date_stop': rec.check_out,
                                                             'work_entry_type_id': 1,
                                                             'name': 'Attendance: '+ rec.employee_id.name})
                rec.write({
                    'is_work_entry':True
                })