from odoo import models, fields, api

class RequestVacation(models.Model):
    _inherit = 'hr.employee'

    def action_open_vacation_wizard(self):
        self.ensure_one()
        return {
            'name':'Request vacation',
            'type': 'ir.actions.act_window',
            'res_model': 'vacation.empl',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_employee_id':self.id,}
        }

