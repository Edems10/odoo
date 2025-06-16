# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'
    _description = 'Extended User with Course Functionality'

    # Teacher fields
    taught_course_ids = fields.One2many(
        'online.course', 'teacher_id', string='Taught Courses'
    )

    taught_course_count = fields.Integer(
        string="Taught Courses",
        compute='_compute_taught_course_count'
    )

    # Student fields  
    enrolled_course_ids = fields.Many2many(
        'online.course',
        'course_student_enrollment_rel',
        'user_id',
        'course_id',
        string='Enrolled Courses',
        compute='_compute_enrolled_courses'
    )

    enrolled_course_count = fields.Integer(
        string="Enrolled Courses",
        compute='_compute_enrolled_course_count'
    )

    # Common course count (role-based)
    course_count = fields.Integer(
        string="Course Count",
        compute='_compute_course_count'
    )

    @api.depends('taught_course_ids')
    def _compute_taught_course_count(self):
        """Count taught courses."""
        for user in self:
            user.taught_course_count = len(user.taught_course_ids)

    def _compute_enrolled_courses(self):
        """Find courses where user is enrolled."""
        for user in self:
            courses = self.env['online.course'].search([
                ('student_ids', 'in', [user.id])
            ])
            user.enrolled_course_ids = courses

    @api.depends('enrolled_course_ids')
    def _compute_enrolled_course_count(self):
        """Count enrolled courses."""
        for user in self:
            user.enrolled_course_count = len(user.enrolled_course_ids)

    @api.depends('taught_course_count', 'enrolled_course_count')
    def _compute_course_count(self):
        """Compute total course count based on user role."""
        for user in self:
            if user.has_group('online_course.group_online_course_teacher'):
                user.course_count = user.taught_course_count
            elif user.has_group('online_course.group_online_course_student'):
                user.course_count = user.enrolled_course_count
            else:
                user.course_count = 0

    def _get_course_action(self, name, domain, context=None):
        """Common method for course actions."""
        self.ensure_one()
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'res_model': 'online.course',
            'view_mode': 'kanban,list,form',
            'domain': domain,
            'context': context or {}
        }

    def action_view_taught_courses(self):
        """View courses I teach."""
        return self._get_course_action(
            name='Courses I Teach',
            domain=[('teacher_id', '=', self.id)],
            context={'default_teacher_id': self.id}
        )

    def action_view_enrolled_courses(self):
        """View courses I'm enrolled in."""
        return self._get_course_action(
            name='My Enrolled Courses',
            domain=[('student_ids', 'in', [self.id])]
        )

    def action_view_courses(self):
        """Dynamic course view based on user role."""
        self.ensure_one()
        
        if self.has_group('online_course.group_online_course_teacher'):
            return self.action_view_taught_courses()
        elif self.has_group('online_course.group_online_course_student'):
            return self.action_view_enrolled_courses()
        else:
            return self._get_course_action(
                name='All Courses',
                domain=[('state', '=', 'published')]
            )
