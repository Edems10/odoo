from typing import Any, Dict, List, Literal, Optional, Union
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError

from ..static.constants import CourseConstants
from ..services.course_services import (
    CourseSecurityService,
    CourseEnrollmentService,
    CourseStateService,
)


class Course(models.Model):
    _name: Optional[str] = "online.course"
    _description: Optional[str] = "Online Course"

    name: fields.Char = fields.Char(
        string="Course Name", required=True, help="The name of the course"
    )
    description: fields.Text = fields.Text(string="Description")
    price: fields.Float = fields.Float(
        string="Price",
        default=CourseConstants.DEFAULT_PRICE,
        help="Course price in company currency",
    )
    teacher_id: fields.Many2one = fields.Many2one(
        "res.users",
        string="Teacher",
        required=True,
        help="The instructor for this course",
    )
    student_ids: fields.Many2many = fields.Many2many(
        "res.users", string="Students", help="Students enrolled in this course"
    )
    state: fields.Selection = fields.Selection(
        CourseConstants.States.ALL,
        string="Status",
        default=CourseConstants.States.DRAFT,
        help="Current status of the course",
    )

    can_edit_course_details: fields.Boolean = fields.Boolean(
        compute="_compute_can_edit_course_details",
        help="Whether current user can edit course details",
    )
    can_edit_price: fields.Boolean = fields.Boolean(
        compute="_compute_can_edit_price",
        help="Whether current user can edit course price",
    )
    can_edit_teacher: fields.Boolean = fields.Boolean(
        compute="_compute_can_edit_teacher",
        help="Whether current user can change teacher assignment",
    )
    allow_new_enrollment: fields.Boolean = fields.Boolean(
        compute="_compute_allow_new_enrollment",
        store=True,
        help="Whether the course accepts new enrollments",
    )
    enrolled_count: fields.Integer = fields.Integer(
        compute="_compute_enrolled_count", help="Number of enrolled students"
    )
    is_free: fields.Boolean = fields.Boolean(
        compute="_compute_is_free", store=True, help="Whether the course is free"
    )
    course_type_display: fields.Char = fields.Char(
        compute="_compute_course_type_display", help="Display string for course type"
    )

    @api.depends("teacher_id")
    def _compute_can_edit_course_details(self) -> None:
        security_service: CourseSecurityService = self._get_security_service()
        course: "Course"
        for course in self:
            course.can_edit_course_details = security_service.can_edit_course_details(
                course
            )

    @api.depends("teacher_id")
    def _compute_can_edit_price(self) -> None:
        security_service: CourseSecurityService = self._get_security_service()
        course: "Course"
        for course in self:
            course.can_edit_price = security_service.can_edit_price(course)

    @api.depends("teacher_id")
    def _compute_can_edit_teacher(self) -> None:
        security_service: CourseSecurityService = self._get_security_service()
        course: "Course"
        for course in self:
            course.can_edit_teacher = security_service.can_edit_teacher(course)

    @api.depends("state")
    def _compute_allow_new_enrollment(self) -> None:
        course: "Course"
        for course in self:
            course.allow_new_enrollment = (
                course.state == CourseConstants.States.PUBLISHED
            )

    @api.depends("student_ids")
    def _compute_enrolled_count(self) -> None:
        course: "Course"
        for course in self:
            course.enrolled_count = len(course.student_ids)

    @api.depends("price")
    def _compute_is_free(self) -> None:
        course: "Course"
        for course in self:
            course.is_free = course.price == CourseConstants.MIN_PRICE

    @api.depends("is_free", "price")
    def _compute_course_type_display(self) -> None:
        course: "Course"
        for course in self:
            if course.is_free:
                course.course_type_display = "🆓 FREE COURSE"
            else:
                course.course_type_display = f"💰 PAID COURSE (${course.price:.2f})"

    def _get_security_service(self) -> CourseSecurityService:
        return CourseSecurityService(self.env)

    def _get_enrollment_service(self) -> CourseEnrollmentService:
        return CourseEnrollmentService(self.env)

    def _get_state_service(self) -> CourseStateService:
        return CourseStateService(self.env)

    @api.model_create_multi
    def create(
        self, vals_list: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> "Course":
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        for vals in vals_list:
            if "teacher_id" not in vals or not vals.get("teacher_id"):
                vals["teacher_id"] = self.env.user.id

        return super().create(vals_list)

    def write(self, vals: Dict[str, Any]) -> Literal[True]:
        if not self:
            return super().write(vals)

        security_service: CourseSecurityService = self._get_security_service()

        course: "Course"
        for course in self:
            if "teacher_id" in vals:
                if not security_service.can_edit_teacher(course):
                    raise AccessError(
                        _("Only administrators can reassign course teachers.")
                    )

            restricted_fields: List[str] = ["name", "description", "price"]
            if any(field in vals for field in restricted_fields):
                if not security_service.can_edit_course_details(course):
                    raise AccessError(
                        _(
                            "Only administrators and course creators can edit course details."
                        )
                    )

        return super().write(vals)

    @api.constrains("teacher_id", "student_ids")
    def _check_teacher_not_in_students(self) -> None:
        course: "Course"
        for course in self:
            if course.teacher_id and course.teacher_id in course.student_ids:
                raise ValidationError(
                    _("A teacher cannot be a student of their own course.")
                )

    @api.constrains("price")
    def _check_price_positive(self) -> None:
        course: "Course"
        for course in self:
            if course.price < CourseConstants.MIN_PRICE:
                raise ValidationError(_(CourseConstants.Messages.NEGATIVE_PRICE_ERROR))

    def action_publish(self) -> bool:
        state_service: CourseStateService = self._get_state_service()
        course: "Course"
        for course in self:
            state_service.publish_course(course)
        return True

    def action_close_enrollment(self) -> bool:
        state_service: CourseStateService = self._get_state_service()
        course: "Course"
        for course in self:
            state_service.close_enrollment(course)
        return True

    def action_reopen_enrollment(self) -> bool:
        state_service: CourseStateService = self._get_state_service()
        course: "Course"
        for course in self:
            state_service.reopen_enrollment(course)
        return True

    def action_archive(self) -> bool:
        state_service: CourseStateService = self._get_state_service()
        course: "Course"
        for course in self:
            state_service.archive_course(course)
        return True

    def action_draft(self) -> bool:
        state_service: CourseStateService = self._get_state_service()
        course: "Course"
        for course in self:
            state_service.set_to_draft(course)
        return True

    def action_self_enroll(self) -> Dict[str, Any]:
        self.ensure_one()
        enrollment_service: CourseEnrollmentService = self._get_enrollment_service()
        return enrollment_service.enroll_student(self, self.env.user)

    def action_self_unenroll(self) -> Dict[str, Any]:
        self.ensure_one()
        enrollment_service: CourseEnrollmentService = self._get_enrollment_service()
        return enrollment_service.unenroll_student(self, self.env.user)

    def action_view_students(self) -> Dict[str, Any]:
        self.ensure_one()
        return {
            "name": _("Enrolled Students"),
            "type": "ir.actions.act_window",
            "res_model": "res.users",
            "view_mode": "list,form",
            "domain": [("id", "in", self.student_ids.ids)],
            "context": {},
        }
