# -*- coding: utf-8 -*-
from odoo.api import Environment
from ..static.constants import CourseConstants


class UserCourseService:
    """Service for handling user-course relationships."""

    def __init__(self, env: Environment) -> None:
        self.env = env
        self.course_model = env["online.course"]

    def get_user_enrolled_courses(self, user):
        """Get courses where user is enrolled as student."""
        return self.course_model.search([("student_ids", "in", [user.id])])

    def get_user_course_count(self, user):
        """Get course count based on user role."""
        if user.has_group(CourseConstants.Security.TEACHER_GROUP):
            return user.taught_course_count
        elif user.has_group(CourseConstants.Security.STUDENT_GROUP):
            return user.enrolled_course_count
        else:
            return 0

    def get_taught_courses_action(self, user):
        """Get action to view taught courses."""
        user.ensure_one()
        return self._create_course_action(
            name="Courses I Teach",
            domain=[("teacher_id", "=", user.id)],
            context={"default_teacher_id": user.id},
        )

    def get_enrolled_courses_action(self, user):
        """Get action to view enrolled courses."""
        user.ensure_one()
        return self._create_course_action(
            name="My Enrolled Courses", domain=[("student_ids", "in", [user.id])]
        )

    def get_user_courses_action(self, user):
        """Get dynamic course action based on user role."""
        user.ensure_one()

        if user.has_group(CourseConstants.Security.TEACHER_GROUP):
            return self.get_taught_courses_action(user)
        elif user.has_group(CourseConstants.Security.STUDENT_GROUP):
            return self.get_enrolled_courses_action(user)
        else:
            return self._create_course_action(
                name="All Courses",
                domain=[("state", "=", CourseConstants.States.PUBLISHED)],
            )

    def _create_course_action(self, name, domain, context=None):
        """Create standard course action."""
        return {
            "name": name,
            "type": "ir.actions.act_window",
            "res_model": "online.course",
            "view_mode": "kanban,list,form",
            "domain": domain,
            "context": context or {},
        }
