# -*- coding: utf-8 -*-
from typing import Any, Dict
from odoo import models, fields, api
from ..services.user_services import UserCourseService


class ResUsers(models.Model):
    """Extended User model with course functionality."""

    _inherit = "res.users"
    _description = "Extended User with Course Functionality"

    # ===== COURSE-RELATED FIELDS =====
    taught_course_ids = fields.One2many(
        "online.course",
        "teacher_id",
        string="Courses as Teacher",
        help="Courses where this user is the teacher",
    )

    taught_course_count = fields.Integer(
        string="Taught Courses Count",
        compute="_compute_taught_course_count",
        help="Number of courses this user teaches",
    )

    enrolled_course_ids = fields.Many2many(
        "online.course",
        "course_student_enrollment_rel",
        "user_id",
        "course_id",
        string="Enrolled Courses",
        compute="_compute_enrolled_courses",
        help="Courses where this user is enrolled as a student",
    )

    enrolled_course_count = fields.Integer(
        string="Enrolled Courses Count",
        compute="_compute_enrolled_course_count",
        help="Number of courses this user is enrolled in",
    )

    course_count = fields.Integer(
        string="Course Count",
        compute="_compute_course_count",
        help="Total course count based on user role",
    )

    # ===== COMPUTE METHODS =====
    @api.depends("taught_course_ids")
    def _compute_taught_course_count(self) -> None:
        """Count taught courses efficiently."""
        for user in self:
            user.taught_course_count = len(user.taught_course_ids)

    def _compute_enrolled_courses(self) -> None:
        """Find courses where user is enrolled as student."""
        course_service = self._get_course_service()
        for user in self:
            user.enrolled_course_ids = course_service.get_user_enrolled_courses(user)

    @api.depends("enrolled_course_ids")
    def _compute_enrolled_course_count(self) -> None:
        for user in self:
            user.enrolled_course_count = len(user.enrolled_course_ids)

    @api.depends("taught_course_count", "enrolled_course_count")
    def _compute_course_count(self) -> None:
        for user in self:
            user.course_count = self._get_course_service().get_user_course_count(user)

    def _get_course_service(self) -> UserCourseService:
        return UserCourseService(self.env)

    # ===== ACTION METHODS =====
    def action_view_taught_courses(self) -> Dict[str, Any]:
        """View courses I teach."""
        return self._get_course_service().get_taught_courses_action(self)

    def action_view_enrolled_courses(self) -> Dict[str, Any]:
        """View courses I'm enrolled in."""
        return self._get_course_service().get_enrolled_courses_action(self)

    def action_view_courses(self) -> Dict[str, Any]:
        """Dynamic course view based on user role."""
        return self._get_course_service().get_user_courses_action(self)
