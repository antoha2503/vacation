from odoo import fields, models, api
from odoo.exceptions import ValidationError

class VacationEmpl(models.TransientModel):
    _name = 'vacation.empl'
    _description = 'Vacation Empl'
    _rec_name = 'employee_id'

    start_date = fields.Date(string='Початкова дата', required=True, default=fields.Date.today)
    end_date = fields.Date(string='Кінечна дата', required=True)
    number_days = fields.Integer(string='Дні', required=True, default=0, readonly=True, compute='_compute_number_days')
    type_statement = fields.Selection([
        ('main_vacation','Заяви на щорічну основну відпустку'),
        ('part_leave','Заяви на частину щорічної відпустки'),
        ('own_account','Заяви на відпустку за власний рахунок'),
        ('birth_child','Заява про відпустку при народженні дитини'),
        ('babysitting','Заява на відпустку для догляду за дитиною'),
    ], default='main_vacation', string="Тип заяви", required=True)

    employee_id = fields.Many2one('hr.employee', string='Співробітник', readonly=True, default=lambda self: self.env.user.employee_id)
    name_company = fields.Many2one('res.company', string='Назва компанії', related='employee_id.company_id')
    parent_id = fields.Many2one('hr.employee', string='Керівник', readonly=False, required=True, compute='_onchange_employee_id')
    department_id = fields.Many2one('hr.department', string='Відділ', required=True, related='employee_id.department_id')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for record in self:
            if record.employee_id and record.employee_id.parent_id:
                record.parent_id = record.employee_id.parent_id
            else:
                record.parent_id = False

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date < record.start_date:
                raise ValidationError("Дата закінчення відпустки не може бути раніше дати її початку!")
            if record.start_date < fields.Date.today():
                raise ValidationError("Не можна оформити відпустку на минулу дату! Виберіть сьогоднішній день або майбутні дати.")

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