# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Course(models.Model):
    _name = 'online.course'
    _description = 'Online Course'

    name = fields.Char(string='Course Name', required=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Price', default=0.0)

    teacher_id = fields.Many2one('res.users', string='Teacher', required=True)
    student_ids = fields.Many2many('res.users', string='Students')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ], string='Status', default='draft')

    @api.constrains('teacher_id', 'student_ids')
    def _check_teacher_not_in_students(self):
        """A teacher cannot be a student of their own course."""
        for course in self:
            if course.teacher_id and course.teacher_id in course.student_ids:
                raise ValidationError("A user cannot be a teacher and a student of the same course.")

    @api.constrains('price')
    def _check_price_positive(self):
        """Course price cannot be negative."""
        for course in self:
            if course.price < 0:
                raise ValidationError("Course price cannot be negative.")


    def action_publish(self):
        """Publish courses with validation."""
        for course in self:
            if course.price < 0:
                raise ValidationError("Cannot publish course with negative price.")
            course.state = 'published'
        return True


    def action_archive(self):
        self.write({'state': 'archived'})

    def action_draft(self):
        self.write({'state': 'draft'})

