# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError

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

    # Security helper fields
    can_edit_course_details = fields.Boolean(
        string='Can Edit Course Details',
        compute='_compute_can_edit_course_details'
    )
    
    can_edit_price = fields.Boolean(
        string='Can Edit Price',
        compute='_compute_can_edit_price'
    )
    
    can_edit_teacher = fields.Boolean(
        string='Can Edit Teacher',
        compute='_compute_can_edit_teacher'
    )

    # Other existing fields...
    allow_new_enrollment = fields.Boolean(
        string='Allow New Enrollment',
        compute='_compute_allow_new_enrollment',
        store=True
    )

    enrolled_count = fields.Integer(
        string='Enrolled Students',
        compute='_compute_enrolled_count'
    )

    is_free = fields.Boolean(string='Is Free Course', compute='_compute_is_free', store=True)
    course_type_display = fields.Char(string='Course Type', compute='_compute_course_type_display')

    @api.depends('teacher_id')
    def _compute_can_edit_course_details(self):
        """Check if current user can edit course name and description."""
        for course in self:
            current_user = self.env.user
            is_admin = current_user.has_group('base.group_system')
            is_course_creator = (course.teacher_id == current_user)
            
            course.can_edit_course_details = is_admin or is_course_creator

    @api.depends('teacher_id')
    def _compute_can_edit_price(self):
        """Check if current user can edit course price."""
        for course in self:
            current_user = self.env.user
            is_admin = current_user.has_group('base.group_system')
            is_course_creator = (course.teacher_id == current_user)
            
            course.can_edit_price = is_admin or is_course_creator

    @api.depends('teacher_id')
    def _compute_can_edit_teacher(self):
        """Check if current user can change teacher assignment."""
        for course in self:
            current_user = self.env.user
            is_admin = current_user.has_group('base.group_system')
            
            course.can_edit_teacher = is_admin

    @api.depends('state')
    def _compute_allow_new_enrollment(self):
        for course in self:
            course.allow_new_enrollment = (course.state == 'published')

    @api.depends('student_ids')
    def _compute_enrolled_count(self):
        for course in self:
            course.enrolled_count = len(course.student_ids)

    @api.depends('price')
    def _compute_is_free(self):
        for course in self:
            course.is_free = (course.price == 0.0)

    @api.depends('is_free')
    def _compute_course_type_display(self):
        for course in self:
            if course.is_free:
                course.course_type_display = "🆓 FREE COURSE"
            else:
                course.course_type_display = f"💰 PAID COURSE (${course.price:.2f})"

    # ✅ AUTO-ASSIGN TEACHER ON CREATION
    @api.model
    def create(self, vals):
        """Override create to auto-assign current user as teacher."""
        # Auto-assign current user as teacher if not specified
        if 'teacher_id' not in vals or not vals.get('teacher_id'):
            vals['teacher_id'] = self.env.user.id
            
        return super(Course, self).create(vals)

    # ✅ IMPROVED WRITE METHOD FOR CREATION AND EDITING
    def write(self, vals):
        """Override write to enforce field-level security."""
        # Allow creation without restrictions
        if not self:  # Creating new record
            return super(Course, self).write(vals)
            
        for course in self:
            current_user = self.env.user
            is_admin = current_user.has_group('base.group_system')
            is_course_creator = (course.teacher_id == current_user)
            
            # Special handling for teacher reassignment
            if 'teacher_id' in vals:
                if not is_admin:
                    raise AccessError("❌ Only administrators can reassign course teachers.")
                # Admin is changing teacher - allow it
                continue
            
            # For other field changes, check permissions
            restricted_fields = ['name', 'description', 'price']
            if any(field in vals for field in restricted_fields):
                if not (is_admin or is_course_creator):
                    raise AccessError("❌ Only administrators and the course creator can edit course details.")
            
            # Allow state changes for teachers (publish, close, etc.)
            # Allow student_ids changes (for enrollment - handled by sudo in methods)
        
        return super(Course, self).write(vals)

    # Constraints
    @api.constrains('teacher_id', 'student_ids')
    def _check_teacher_not_in_students(self):
        for course in self:
            if course.teacher_id and course.teacher_id in course.student_ids:
                raise ValidationError("A teacher cannot be a student of their own course.")

    @api.constrains('price')
    def _check_price_positive(self):
        for course in self:
            if course.price < 0:
                raise ValidationError("Course price cannot be negative.")

    # Course management methods
    def action_publish(self):
        """Publish draft courses."""
        for course in self:
            if course.price < 0:
                raise ValidationError("Cannot publish course with negative price.")
            course.state = 'published'
        return True

    def action_close_enrollment(self):
        """Close enrollment for published courses."""
        for course in self:
            if course.state != 'published':
                raise ValidationError("Can only close enrollment for published courses.")
            course.state = 'closed'
        return True

    def action_reopen_enrollment(self):
        """Reopen enrollment for closed courses."""
        for course in self:
            if course.state != 'closed':
                raise ValidationError("Can only reopen enrollment for closed courses.")
            course.state = 'published'
        return True

    def action_archive(self):
        """Archive courses."""
        for course in self:
            course.state = 'archived'
        return True

    def action_draft(self):
        """Set courses back to draft."""
        for course in self:
            if course.student_ids:
                raise ValidationError(
                    f"Cannot set course '{course.name}' to draft because it has enrolled students."
                )
            course.state = 'draft'
        return True

    def action_self_enroll(self):
        """Allow current user to enroll themselves in the course."""
        self.ensure_one()
        current_user = self.env.user
        
        if self.state != 'published':
            raise ValidationError("❌ Cannot enroll: This course is not currently accepting enrollments.")
        
        if current_user == self.teacher_id:
            raise ValidationError("❌ Teachers cannot enroll in their own courses.")
        
        if current_user in self.student_ids:
            raise ValidationError("❌ You are already enrolled in this course.")
        
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
        
        if current_user not in self.student_ids:
            raise ValidationError("❌ You are not enrolled in this course.")
        
        if current_user == self.teacher_id:
            raise ValidationError("❌ Teachers cannot unenroll from their own courses.")
        
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
