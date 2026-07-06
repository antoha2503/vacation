from odoo import fields, models, api
from odoo.exceptions import ValidationError

class VacationEmpl(models.TransientModel):
    _name = 'vacation.empl'
    _description = 'Vacation Empl'
    _rec_name = 'employee_id'

    start_date = fields.Date(string='Start data', required=True, default=fields.Date.today)
    end_date = fields.Date(string='End data', required=True)
    number_days = fields.Integer(string='Days', required=True, default=0, readonly=True, compute='_compute_number_days')
    type_statement = fields.Selection([
        ('main_vacation','Заяви на щорічну основну відпустку'),
        ('part_leave','Заяви на частину щорічної відпустки'),
        ('own_account','Заяви на відпустку за власний рахунок'),
        ('birth_child','Заява про відпустку при народженні дитини'),
        ('babysitting','Заява на відпустку для догляду за дитиною'),
    ], default='main_vacation', required=True)

    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True, default=lambda self: self.env.user.employee_id)
    name_company = fields.Many2one('res.company', string='Company', related='employee_id.company_id')
    parent_id = fields.Many2one('hr.employee', string='Parent', readonly=False, default=lambda self: self.env.user.employee_id.parent_id)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id')

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date < record.start_date:
                raise ValidationError("Дата окончания отпуска не может быть раньше даты его начала!")
            if record.start_date < fields.Date.today():
                raise ValidationError("Нельзя оформить отпуск на прошедшую дату! Выберите сегодняшний день или будущие даты.")

    @api.depends('start_date', 'end_date')
    def _compute_number_days(self):
        for record in self:
            if record.start_date and record.end_date:
                record.number_days = (record.end_date - record.start_date).days + 1
            else:
                record.number_days = 0


    def action_open_vacation(self):
        self.ensure_one()

        url = "/report/pdf/vacation.report_vacation/%s" % self.id
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new'
        }

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': 'Send mail',
        #         'message': 'Send you on mail',
        #         'type': 'info',
        #         'sticky': False,
        #     }
        # }

    def action_print(self):
        self.ensure_one()
        return self.env.ref('vacation.action_report_vacation').report_action(self)