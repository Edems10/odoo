# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    taught_course_ids = fields.One2many(
        'online.course', 'teacher_id', string='Taught Courses'
    )

    enrolled_course_ids = fields.Many2many(
        'online.course', 
        string='Enrolled Courses',
        compute='_compute_enrolled_courses'
    )

    taught_course_count = fields.Integer(
        string="Taught Courses Count",
        compute='_compute_taught_course_count'
    )

    enrolled_course_count = fields.Integer(
        string="Enrolled Courses Count", 
        compute='_compute_enrolled_course_count'
    )

    @api.depends('taught_course_ids')
    def _compute_taught_course_count(self):
        for user in self:
            user.taught_course_count = len(user.taught_course_ids)

    def _compute_enrolled_courses(self):
        for user in self:
            courses = self.env['online.course'].search([
                ('student_ids', 'in', [user.id])
            ])
            user.enrolled_course_ids = courses

    @api.depends('enrolled_course_ids')
    def _compute_enrolled_course_count(self):
        for user in self:
            user.enrolled_course_count = len(user.enrolled_course_ids)

    def action_view_taught_courses(self):
        self.ensure_one()
        return {
            'name': 'Courses I Teach',
            'type': 'ir.actions.act_window',
            'res_model': 'online.course',
            'view_mode': 'kanban,list,form',
            'domain': [('teacher_id', '=', self.id)],
            'context': {'default_teacher_id': self.id}
        }

    def action_view_enrolled_courses(self):
        self.ensure_one()
        return {
            'name': 'My Enrolled Courses',
            'type': 'ir.actions.act_window',
            'res_model': 'online.course',
            'view_mode': 'kanban,list,form',
            'domain': [('student_ids', 'in', [self.id])],
            'context': {}
        }
