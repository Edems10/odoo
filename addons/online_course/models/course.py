# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Course(models.Model):
    _name = 'online.course'
    _description = 'Online Course'

    name = fields.Char(string='Course Name', required=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Price', default=100.0)

    teacher_id = fields.Many2one('res.users', string='Teacher', required=True)
    student_ids = fields.Many2many('res.users', string='Students')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published - Open for Enrollment'),
        ('closed', 'Published - Enrollment Closed'),
        ('archived', 'Archived - Course Ended'),
    ], string='Status', default='draft')

    # NEW: Control enrollment without hiding course
    allow_new_enrollment = fields.Boolean(
        string='Allow New Enrollment',
        compute='_compute_allow_new_enrollment',
        store=True
    )

    # Keep track of enrollment counts
    enrolled_count = fields.Integer(
        string='Enrolled Students',
        compute='_compute_enrolled_count'
    )

    is_free = fields.Boolean(string='Is Free Course', compute='_compute_is_free', store=True)
    course_type_display = fields.Char(string='Course Type', compute='_compute_course_type_display')

    @api.depends('state')
    def _compute_allow_new_enrollment(self):
        """Compute if new enrollment is allowed based on state."""
        for course in self:
            course.allow_new_enrollment = (course.state == 'published')

    @api.depends('student_ids')
    def _compute_enrolled_count(self):
        """Count enrolled students."""
        for course in self:
            course.enrolled_count = len(course.student_ids)

    @api.depends('price')
    def _compute_is_free(self):
        """Compute if course is free based on price."""
        for course in self:
            course.is_free = (course.price == 0.0)

    @api.depends('is_free')
    def _compute_course_type_display(self):
        """Compute display text for course type."""
        for course in self:
            if course.is_free:
                course.course_type_display = "🆓 FREE COURSE"
            else:
                course.course_type_display = f"💰 PAID COURSE (${course.price:.2f})"

    @api.constrains('teacher_id', 'student_ids')
    def _check_teacher_not_in_students(self):
        """A teacher cannot be a student of their own course."""
        for course in self:
            if course.teacher_id and course.teacher_id in course.student_ids:
                raise ValidationError("A teacher cannot be a student of their own course.")

    @api.constrains('price')
    def _check_price_positive(self):
        """Course price cannot be negative."""
        for course in self:
            if course.price < 0:
                raise ValidationError("Course price cannot be negative.")

    @api.constrains('student_ids', 'allow_new_enrollment')
    def _check_new_enrollment_allowed(self):
        """Prevent NEW enrollment when not allowed, but keep existing students."""
        for course in self:
            if not course.allow_new_enrollment and course.student_ids:
                # Get the student IDs that were just added
                original_students = course._origin.student_ids if course._origin else self.env['res.users']
                new_students = course.student_ids - original_students
                
                if new_students:
                    raise ValidationError(
                        f"❌ Enrollment Closed: '{course.name}' is not accepting new enrollments.\n\n"
                        f"Current status: {dict(course._fields['state'].selection)[course.state]}\n"
                        f"Existing students can continue accessing the course."
                    )

    def action_publish(self):
        """Publish course and open for enrollment."""
        for course in self:
            if course.price < 0:
                raise ValidationError("Cannot publish course with negative price.")
            course.state = 'published'
        return True

    def action_close_enrollment(self):
        """Close enrollment but keep course active for existing students."""
        for course in self:
            if course.state != 'published':
                raise ValidationError("Can only close enrollment for published courses.")
            course.state = 'closed'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Enrollment Closed 🔒',
                'message': f'"{course.name}" is no longer accepting new students. Existing students can continue accessing the course.',
                'type': 'info',
            }
        }

    def action_reopen_enrollment(self):
        """Reopen enrollment for closed courses."""
        for course in self:
            if course.state != 'closed':
                raise ValidationError("Can only reopen enrollment for closed courses.")
            course.state = 'published'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Enrollment Reopened 🎉',
                'message': f'"{course.name}" is now accepting new students again!',
                'type': 'success',
            }
        }

    def action_archive(self):
        """Archive course completely - course has ended."""
        for course in self:
            course.state = 'archived'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Course Archived 📚',
                'message': f'"{course.name}" has been archived. The course has ended.',
                'type': 'info',
            }
        }

    def action_draft(self):
        """Set course back to draft."""
        for course in self:
            if course.student_ids:
                raise ValidationError(
                    f"Cannot set course '{course.name}' to draft because it has enrolled students.\n"
                    f"Please close enrollment first or remove all students."
                )
            course.state = 'draft'
        return True

    def action_self_enroll(self):
        """Allow current user to enroll themselves in the course."""
        self.ensure_one()
        current_user = self.env.user
        
        # Check if course allows enrollment
        if self.state != 'published':
            raise ValidationError("❌ Cannot enroll: This course is not currently accepting enrollments.")
        
        # Check if teacher trying to enroll in own course
        if current_user == self.teacher_id:
            raise ValidationError("❌ Teachers cannot enroll in their own courses.")
        
        # Check if already enrolled
        if current_user in self.student_ids:
            raise ValidationError("❌ You are already enrolled in this course.")
        
        # Use sudo() to bypass record rules for enrollment
        self.sudo().write({'student_ids': [(4, current_user.id)]})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Enrollment Successful! 🎉',
                'message': f'You have been enrolled in "{self.name}"',
                'type': 'success',
            }
        }

    def action_self_unenroll(self):
        """Allow current user to unenroll themselves from the course."""
        self.ensure_one()
        current_user = self.env.user
        
        # Check if enrolled
        if current_user not in self.student_ids:
            raise ValidationError("❌ You are not enrolled in this course.")
        
        # Check if teacher (teachers shouldn't be able to unenroll manually)
        if current_user == self.teacher_id:
            raise ValidationError("❌ Teachers cannot unenroll from their own courses.")
        
        # Use sudo() to bypass record rules for unenrollment
        self.sudo().write({'student_ids': [(3, current_user.id)]})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Unenrolled Successfully',
                'message': f'You have been unenrolled from "{self.name}"',
                'type': 'info',
            }
        }

    # Helper method to check current user enrollment status
    def is_current_user_enrolled(self):
        """Check if current user is enrolled in this course."""
        return self.env.user in self.student_ids

    def can_current_user_enroll(self):
        """Check if current user can enroll in this course."""
        current_user = self.env.user
        return (
            self.state == 'published' and
            current_user != self.teacher_id and
            current_user not in self.student_ids
        )
        
    def action_view_students(self):
        """Action to view enrolled students."""
        self.ensure_one()
        return {
            'name': 'Enrolled Students',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.student_ids.ids)],
            'context': {}
        }
        
    @api.depends('student_ids')
    def _compute_current_user_enrolled(self):
        """Check if current user is enrolled."""
        for course in self:
            course.current_user_enrolled = self.env.user in course.student_ids

    current_user_enrolled = fields.Boolean(
        string='Current User Enrolled',
        compute='_compute_current_user_enrolled'
    )
