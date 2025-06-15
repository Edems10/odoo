from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    # An inverse One2many relationship to easily find a teacher's courses
    taught_course_ids = fields.One2many(
        'online.course', 'teacher_id', string='Taught Courses'
    )

    course_count = fields.Integer(
        string="Course Count",
        compute='_compute_course_count'
    )

    @api.depends('taught_course_ids')
    def _compute_course_count(self):
        for user in self:
            user.course_count = len(user.taught_course_ids)

    def action_view_courses(self):
        """Action for the smart button to show the user's courses."""
        self.ensure_one()
        return {
            'name': 'Taught Courses',
            'type': 'ir.actions.act_window',
            'res_model': 'online.course',
            'view_mode': 'kanban,tree,form',
            'domain': [('teacher_id', '=', self.id)],
            'context': {'default_teacher_id': self.id}
        }
